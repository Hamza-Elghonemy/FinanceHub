import json
import os
from pathlib import Path
from datetime import datetime

def combine_sector_data(healthcare_folder, tech_folder, output_file="combined_financial_data.json"):
    """
    Combines Healthcare and Tech sector data into a single JSON file
    following the structure: {sector: [{company: [{year: [{quarter: {metrics}}]}]}]}
    """
    
    def process_sector_folder(folder_path, sector_name):
        """Process all JSON files in a sector folder and return structured data"""
        sector_data = []
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            print(f"Warning: {sector_name} folder '{folder_path}' does not exist")
            return sector_data
        
        # Get all JSON files in the folder
        json_files = list(folder_path.glob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    company_data = json.load(f)
                
                # Extract company name from company_info or filename
                company_name = company_data.get("company_info", {}).get("symbol", json_file.stem.replace("_consolidated", ""))
                
                # Process company data structure
                company_entry = process_company_data(company_data, company_name)
                if company_entry and company_name in company_entry and company_entry[company_name]:
                    sector_data.append(company_entry)
                    print(f"✅ Processed {company_name}")
                else:
                    print(f"⚠️ No data processed for {company_name}")
                    
            except Exception as e:
                print(f"❌ Error processing {json_file}: {str(e)}")
                continue
        
        return sector_data
    
    def process_company_data(company_data, company_name):
        """Convert company data to the required format"""
        company_entry = {company_name: []}
        
        # Extract the existing ratios from the company data
        company_ratios = company_data.get("ratios", {})
        
        # Check if the data has quarterly structure (your actual structure)
        if "quarterly" in company_data:
            # Group quarters by year
            years_data = {}
            
            for date_key, quarter_data in company_data["quarterly"].items():
                # Parse year and quarter from date like "2025-06-30"
                try:
                    date_obj = datetime.strptime(date_key, "%Y-%m-%d")
                    year = date_obj.year
                    
                    # Determine quarter based on month
                    month = date_obj.month
                    if month <= 3:
                        quarter = 1
                    elif month <= 6:
                        quarter = 2
                    elif month <= 9:
                        quarter = 3
                    else:
                        quarter = 4
                    
                    if year not in years_data:
                        years_data[year] = []
                    
                    # Extract financial metrics (without summary)
                    quarter_metrics = extract_quarter_metrics(quarter_data)
                    
                    years_data[year].append({
                        str(quarter): quarter_metrics
                    })
                    
                except ValueError as e:
                    print(f"Error parsing date {date_key}: {e}")
                    continue
            
            # Convert years_data to the required format and add ratios at year level
            for year, quarters in sorted(years_data.items()):
                year_entry = {
                    str(year): quarters,
                    "ratios": company_ratios  # Add the ratios from the consolidated file
                }
                company_entry[company_name].append(year_entry)
        
        else:
            print(f"Warning: No quarterly data found for {company_name}")
        
        return company_entry
    
    def extract_quarter_metrics(quarter_data):
        """Extract financial metrics from the quarter data (without summary)"""
        metrics = {}
        
        # Extract from profitability section
        profitability = quarter_data.get("profitability", {})
        if profitability:
            metrics["profitability"] = {
                "revenue": int(profitability.get("Revenue", 0)) if profitability.get("Revenue") else 0,
                "gross_profit": int(profitability.get("GrossProfit", 0)) if profitability.get("GrossProfit") else 0,
                "operating_income": int(profitability.get("OperatingIncome", 0)) if profitability.get("OperatingIncome") else 0,
                "net_income": int(profitability.get("NetIncome", 0)) if profitability.get("NetIncome") else 0
            }
        
        # Extract from balance sheet section
        balance_sheet = quarter_data.get("balance_sheet", {})
        if balance_sheet:
            metrics["balance_sheet"] = {
                "cash_and_equivalents": int(balance_sheet.get("CashAndEquivalents", 0)) if balance_sheet.get("CashAndEquivalents") else 0,
                "total_assets": int(balance_sheet.get("TotalAssets", 0)) if balance_sheet.get("TotalAssets") else 0,
                "total_liabilities": int(balance_sheet.get("TotalLiabilities", 0)) if balance_sheet.get("TotalLiabilities") else 0,
                "shareholders_equity": int(balance_sheet.get("ShareholdersEquity", 0)) if balance_sheet.get("ShareholdersEquity") else 0,
                "long_term_debt": int(balance_sheet.get("LongTermDebt", 0)) if balance_sheet.get("LongTermDebt") else 0,
                "current_assets": int(balance_sheet.get("CurrentAssets", 0)) if balance_sheet.get("CurrentAssets") else 0,
                "current_liabilities": int(balance_sheet.get("CurrentLiabilities", 0)) if balance_sheet.get("CurrentLiabilities") else 0
            }
        
        # Extract from cash flow section
        cash_flow = quarter_data.get("cash_flow", {})
        if cash_flow:
            metrics["cash_flow"] = {
                "operating_cash_flow": int(cash_flow.get("OperatingCashFlow", 0)) if cash_flow.get("OperatingCashFlow") else 0,
                "capex": int(cash_flow.get("CapEx", 0)) if cash_flow.get("CapEx") else 0,
                "free_cash_flow": int(cash_flow.get("FreeCashFlow", 0)) if cash_flow.get("FreeCashFlow") else 0,
                "earnings_quality": round(cash_flow.get("EarningsQuality", 0), 2) if cash_flow.get("EarningsQuality") else 0
            }
        
        return metrics
    
    # Process both sectors
    print("Processing Healthcare sector data...")
    healthcare_data = process_sector_folder(healthcare_folder, "Healthcare")
    
    print("\nProcessing Tech sector data...")
    tech_data = process_sector_folder(tech_folder, "Tech")
    
    # Combine into final structure
    combined_data = {
        "Healthcare": healthcare_data,
        "Tech": tech_data
    }
    
    # Save to output file
    output_path = Path(output_file)
    os.makedirs(output_path.parent, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(combined_data, f, indent=4)
    
    print(f"\n✅ Combined data saved to {output_path}")
    print(f"📊 Healthcare companies: {len(healthcare_data)}")
    print(f"💻 Tech companies: {len(tech_data)}")
    
    return combined_data

def validate_combined_data(file_path):
    """Validate the structure of the combined data file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print("\n📋 Data Structure Validation:")
        
        for sector_name, sector_data in data.items():
            print(f"\n{sector_name} Sector:")
            print(f"  Companies: {len(sector_data)}")
            
            for company_entry in sector_data:
                for company_name, company_data in company_entry.items():
                    years = len(company_data)
                    total_quarters = 0
                    for year_data in company_data:
                        for year_key, year_content in year_data.items():
                            if year_key != "ratios":  # Skip ratios when counting quarters
                                total_quarters += len(year_content)
                    print(f"    {company_name}: {years} years, {total_quarters} quarters")
                    
                    # Show sample for first company
                    if company_name == list(company_entry.keys())[0] and sector_name == "Healthcare":
                        first_year = company_data[0]
                        print(f"      Available sections: {list(first_year.keys())}")
                        if "ratios" in first_year:
                            ratios = first_year["ratios"]
                            print(f"      Company ratios: {list(ratios.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {str(e)}")
        return False

if __name__ == "__main__":
    # Define folder paths based on your structure
    healthcare_folder = "data/preprocessed_data/HealthCare"
    tech_folder = "data/preprocessed_data/Tech"
    output_file = "data/combined_financial_data_yearly_ratios.json"
    
    # Combine the data
    combined_data = combine_sector_data(healthcare_folder, tech_folder, output_file)
    
    # Validate the result
    if os.path.exists(output_file):
        validate_combined_data(output_file)
    
    print("\n🎯 Data preprocessing with yearly ratios completed!")