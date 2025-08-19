import json


def clean_and_consolidate(bs_data, is_data, cf_data, overview_data, years_to_keep=[2023, 2024, 2025]):
    """
    Consolidate AlphaVantage Balance Sheet, Income Statement, Cash Flow, and Overview 
    into a single cleaned JSON with only key metrics and ratios for given years.
    """

    def parse_year(date_str):
        """Extract year from a YYYY-MM-DD date string."""
        try:
            return int(date_str.split("-")[0])
        except Exception:
            return None

    # Filter annual reports to only target years
    annual_bs = [r for r in bs_data.get("annualReports", []) if parse_year(r.get("fiscalDateEnding", "")) in years_to_keep]
    annual_is = [r for r in is_data.get("annualReports", []) if parse_year(r.get("fiscalDateEnding", "")) in years_to_keep]
    annual_cf = [r for r in cf_data.get("annualReports", []) if parse_year(r.get("fiscalDateEnding", "")) in years_to_keep]

    # Filter quarterly reports to only target years
    quarterly_bs = [r for r in bs_data.get("quarterlyReports", []) if parse_year(r.get("fiscalDateEnding", "")) in years_to_keep]
    quarterly_is = [r for r in is_data.get("quarterlyReports", []) if parse_year(r.get("fiscalDateEnding", "")) in years_to_keep]
    quarterly_cf = [r for r in cf_data.get("quarterlyReports", []) if parse_year(r.get("fiscalDateEnding", "")) in years_to_keep]

    def clean_single(bs, is_, cf):
        """Helper to clean a single period’s financials."""
        cleaned = {
            "profitability": {
                "Revenue": float(is_.get("totalRevenue", 0)) if is_.get("totalRevenue") else None,
                "GrossProfit": float(is_.get("grossProfit", 0)) if is_.get("grossProfit") else None,
                "OperatingIncome": float(is_.get("operatingIncome", 0)) if is_.get("operatingIncome") else None,
                "NetIncome": float(is_.get("netIncome", 0)) if is_.get("netIncome") else None,
                "EPS_Basic": float(is_.get("reportedEPS", 0)) if is_.get("reportedEPS") else None,
            },
            "balance_sheet": {
                "CashAndEquivalents": float(bs.get("cashAndCashEquivalentsAtCarryingValue", 0)) if bs.get("cashAndCashEquivalentsAtCarryingValue") else None,
                "TotalAssets": float(bs.get("totalAssets", 0)) if bs.get("totalAssets") else None,
                "TotalLiabilities": float(bs.get("totalLiabilities", 0)) if bs.get("totalLiabilities") else None,
                "ShareholdersEquity": float(bs.get("totalShareholderEquity", 0)) if bs.get("totalShareholderEquity") else None,
                "LongTermDebt": float(bs.get("longTermDebt", 0)) if bs.get("longTermDebt") else None,
                "CurrentAssets": float(bs.get("totalCurrentAssets", 0)) if bs.get("totalCurrentAssets") else None,
                "CurrentLiabilities": float(bs.get("totalCurrentLiabilities", 0)) if bs.get("totalCurrentLiabilities") else None,
            },
            "cash_flow": {
                "OperatingCashFlow": float(cf.get("operatingCashflow", 0)) if cf.get("operatingCashflow") else None,
                "CapEx": float(cf.get("capitalExpenditures", 0)) if cf.get("capitalExpenditures") else None,
                "FreeCashFlow": None,
                "EarningsQuality": None,
            },
        }

        # Compute Free Cash Flow
        cfo = cleaned["cash_flow"]["OperatingCashFlow"]
        capex = cleaned["cash_flow"]["CapEx"]
        if cfo is not None and capex is not None:
            cleaned["cash_flow"]["FreeCashFlow"] = cfo - abs(capex)

        # Compute Earnings Quality
        ni = cleaned["profitability"]["NetIncome"]
        if ni and cfo:
            cleaned["cash_flow"]["EarningsQuality"] = round(cfo / ni, 2)

        # Strip empty (None) fields
        for section in ["profitability", "balance_sheet", "cash_flow"]:
            cleaned[section] = {k: v for k, v in cleaned[section].items() if v is not None}

        return cleaned

    # Build annual and quarterly dictionaries
    annual_cleaned = {}
    for bs, is_, cf in zip(annual_bs, annual_is, annual_cf):
        year = parse_year(bs.get("fiscalDateEnding", "")) or parse_year(is_.get("fiscalDateEnding", "")) or parse_year(cf.get("fiscalDateEnding", ""))
        if year:
            annual_cleaned[year] = clean_single(bs, is_, cf)

    quarterly_cleaned = {}
    for bs, is_, cf in zip(quarterly_bs, quarterly_is, quarterly_cf):
        date = bs.get("fiscalDateEnding") or is_.get("fiscalDateEnding") or cf.get("fiscalDateEnding")
        if date:
            quarterly_cleaned[date] = clean_single(bs, is_, cf)

    # Final consolidated structure
    cleaned = {
        "company_info": {
            "symbol": overview_data.get("Symbol"),
            "name": overview_data.get("Name"),
            "cik": overview_data.get("CIK"),
            "exchange": overview_data.get("Exchange"),
            "sector": overview_data.get("Sector"),
            "industry": overview_data.get("Industry"),
            "fiscal_year_end": overview_data.get("FiscalYearEnd"),
            "country": overview_data.get("Country"),
            "market_cap": overview_data.get("MarketCapitalization"),
        },
        "annual": annual_cleaned,
        "quarterly": quarterly_cleaned,
        "ratios": {
            "PE_Ratio": float(overview_data.get("PERatio", 0)) if overview_data.get("PERatio") else None,
            "PEG_Ratio": float(overview_data.get("PEGRatio", 0)) if overview_data.get("PEGRatio") else None,
            "PriceToBook": float(overview_data.get("PriceToBookRatio", 0)) if overview_data.get("PriceToBookRatio") else None,
            "ProfitMargin": float(overview_data.get("ProfitMargin", 0)) if overview_data.get("ProfitMargin") else None,
            "ReturnOnAssets": float(overview_data.get("ReturnOnAssetsTTM", 0)) if overview_data.get("ReturnOnAssetsTTM") else None,
            "ReturnOnEquity": float(overview_data.get("ReturnOnEquityTTM", 0)) if overview_data.get("ReturnOnEquityTTM") else None,
            "DividendYield": float(overview_data.get("DividendYield", 0)) if overview_data.get("DividendYield") else None,
        }
    }

    # Strip empty ratios
    cleaned["ratios"] = {k: v for k, v in cleaned["ratios"].items() if v is not None}

    return cleaned


if __name__ == "__main__":
    company_symbols = ["AAPL", "MSFT","GOOGL","IBM","META"]
    financial_statements = ["BALANCE_SHEET", "INCOME_STATEMENT", "CASH_FLOW","OVERVIEW"]
    for company_symbol in company_symbols:
        fin_statement = []
        for statement in financial_statements:
                with open(f"{company_symbol}_{statement}.json") as f: fin_statement.append(json.load(f))
        consolidated = clean_and_consolidate(fin_statement[0], fin_statement[1], fin_statement[2], fin_statement[3])
        with open(f"{company_symbol}_consolidated.json", "w") as f:
            json.dump(consolidated, f, indent=2)

    print("✅ Clean consolidated financials (2023–2025 only) saved to financials_consolidated.json")
