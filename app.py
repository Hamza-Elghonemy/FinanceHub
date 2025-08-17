import os
import pandas as pd
import json

def build_json_from_folders(base_path, output_file="package.json"):
    sectors = {}  

    for sector in os.listdir(base_path):
        sector_path = os.path.join(base_path, sector)
        if not os.path.isdir(sector_path):
            continue

        companies = []

        for file in os.listdir(sector_path):
            if not file.endswith(".csv"):
                continue

            company_name = os.path.splitext(file)[0]
            file_path = os.path.join(sector_path, file)

            df = pd.read_csv(file_path)

            years = []
            for _, row in df.iterrows():
                year = str(row.iloc[0])      # first column = year
                quarter = str(row.iloc[1])   # second column = quarter
                features = {
                    col: (row[col].item() if hasattr(row[col], "item") else row[col])
                    for col in df.columns[2:]
                }

                # check if this year already exists
                year_obj = next((y for y in years if year in y), None)
                if year_obj:
                    year_obj[year].append({quarter: features})
                else:
                    years.append({year: [{quarter: features}]})

            companies.append({company_name: years})

        sectors[sector] = companies

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sectors, f, indent=4, ensure_ascii=False)

    return sectors

base_path = "data" 
json_data = build_json_from_folders(base_path)
print(json.dumps(json_data, indent=4))
