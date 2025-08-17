import json

def clean_financials(report_data):
    """Extract and clean only key financial metrics for AI insights."""
    
    # Check if report_data has the expected structure
    if not report_data or 'bs' not in report_data:
        print("Warning: No balance sheet data found")
        return None

    # Build lookup maps for bs, ic, cf
    bs = {item.get("concept", ""): item.get("value") for item in report_data.get("bs", [])}
    ic = {item.get("concept", ""): item.get("value") for item in report_data.get("ic", [])}
    cf = {item.get("concept", ""): item.get("value") for item in report_data.get("cf", [])}

    cleaned = {
        "Profitability": {
            "Revenue": ic.get("us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax"),
            "GrossProfit": ic.get("us-gaap_GrossProfit"),
            "OperatingIncome": ic.get("us-gaap_OperatingIncomeLoss"),
            "NetIncome": ic.get("us-gaap_NetIncomeLoss"),
            "EPS_Basic": ic.get("us-gaap_EarningsPerShareBasic"),
            "EPS_Diluted": ic.get("us-gaap_EarningsPerShareDiluted"),
        },
        "BalanceSheet": {
            "CashAndEquivalents": bs.get("us-gaap_CashAndCashEquivalentsAtCarryingValue"),
            "MarketableSecurities": bs.get("us-gaap_MarketableSecuritiesCurrent"),
            "TotalAssets": bs.get("us-gaap_Assets"),
            "TotalLiabilities": bs.get("us-gaap_Liabilities"),
            "ShareholdersEquity": bs.get("us-gaap_StockholdersEquity"),
            "LongTermDebt": bs.get("us-gaap_LongTermDebtNoncurrent"),
            "CurrentAssets": bs.get("us-gaap_AssetsCurrent"),
            "CurrentLiabilities": bs.get("us-gaap_LiabilitiesCurrent"),
        },
        "CashFlow": {
            "OperatingCashFlow": cf.get("us-gaap_NetCashProvidedByUsedInOperatingActivities"),
            "CapEx": cf.get("us-gaap_PaymentsToAcquirePropertyPlantAndEquipment"),
            "FreeCashFlow": None,
            "Change_AR": cf.get("us-gaap_IncreaseDecreaseInAccountsReceivable"),
            "Change_AP": cf.get("us-gaap_IncreaseDecreaseInAccountsPayable"),
            "Change_Inventory": cf.get("us-gaap_IncreaseDecreaseInInventories"),
            "Change_OtherAssets": cf.get("us-gaap_IncreaseDecreaseInOtherOperatingAssets"),
            "Change_OtherLiabilities": cf.get("us-gaap_IncreaseDecreaseInOtherOperatingLiabilities"),
        },
    }

    # Calculate Free Cash Flow
    cfo = cleaned["CashFlow"]["OperatingCashFlow"]
    capex = cleaned["CashFlow"]["CapEx"]
    if cfo is not None and capex is not None:
        cleaned["CashFlow"]["FreeCashFlow"] = cfo - abs(capex)  # CapEx is usually negative

    # Add earnings quality check
    ni = cleaned["Profitability"]["NetIncome"]
    if ni and cfo:
        cleaned["CashFlow"]["EarningsQuality"] = round(cfo / ni, 2)

    return cleaned


def process_all_quarters(data):
    """Process all quarters and organize by company information."""
    
    if not data.get("data") or len(data["data"]) == 0:
        print("❌ No financial data found")
        return None
    
    # Extract company information from the first record
    first_record = data["data"][0]
    company_info = {
        "cik": data.get("cik"),
        "symbol": data.get("symbol"),
        "company_name": f"{data.get('symbol')} Inc."  # You can enhance this with actual company name
    }
    
    # Process each quarter
    quarterly_data = {}
    
    for record in data["data"]:
        year = record.get("year")
        quarter = record.get("quarter")
        quarter_key = f"{year}_Q{quarter}"
        
        # Clean the financial data for this quarter
        cleaned_financials = clean_financials(record.get("report", {}))
        
        if cleaned_financials:
            quarterly_data[quarter_key] = {
                "period_info": {
                    "year": year,
                    "quarter": quarter,
                    "form": record.get("form"),
                    "start_date": record.get("startDate"),
                    "end_date": record.get("endDate"),
                    "filed_date": record.get("filedDate"),
                    "access_number": record.get("accessNumber")
                },
                "financials": cleaned_financials
            }
    
    # Combine everything into final structure
    result = {
        "company_info": company_info,
        "quarters": quarterly_data,
        "metadata": {
            "total_quarters": len(quarterly_data),
            "date_range": {
                "earliest": min([q["period_info"]["start_date"] for q in quarterly_data.values()]),
                "latest": max([q["period_info"]["end_date"] for q in quarterly_data.values()])
            },
            "last_updated": "2025-08-17"
        }
    }
    
    return result


if __name__ == "__main__":
    # Load your original JSON
    with open("output/financials_reported.json", "r") as f:
        data = json.load(f)
    
    # Process all quarters
    processed_data = process_all_quarters(data)
    
    if processed_data:
        # Save the new structured JSON
        with open("financials_cleaned.json", "w") as f:
            json.dump(processed_data, f, indent=2)
        
        print("✅ Cleaned financials with quarterly structure saved to financials_cleaned.json")
        print(f"📊 Processed {processed_data['metadata']['total_quarters']} quarters")
        print(f"🏢 Company: {processed_data['company_info']['symbol']} (CIK: {processed_data['company_info']['cik']})")
        
        # Show available quarters
        quarters = list(processed_data['quarters'].keys())
        print(f"📅 Available quarters: {', '.join(sorted(quarters, reverse=True)[:5])}..." if len(quarters) > 5 else f"📅 Available quarters: {', '.join(sorted(quarters, reverse=True))}")
        
    else:
        print("❌ Failed to process financial data")