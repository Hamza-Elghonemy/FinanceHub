import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from prompt_engineering import prompt_Company,prompt_allCompanies 

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

with open(r"./data/combined_financial_data_yearly_ratios.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)

sector_choice = input("Enter sector (Tech or Healthcare): ").strip().capitalize()
company_choice = input("Enter company symbol (e.g., AAPL, MSFT): ").strip().upper()
topic_choice = input("Enter metric (Revenue, Gross_Profit, Operating_Income, Net_Income, etc.): ").strip()
scope_choice = input("Enter analysis scope (Company or Sector): ").strip().capitalize()

sector_data = {sector_choice: all_data[sector_choice]}
prompt = prompt_Company(company_choice, topic_choice)
if(scope_choice == "Sector"):
    prompt = prompt_allCompanies(topic_choice)

sector_json = json.dumps(sector_data, indent=2)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": sector_json}
    ],
    temperature=0
)
 
output_text = response.choices[0].message.content
output_file = os.path.join("output", f"{company_choice}_{topic_choice}_{scope_choice}_analysis.json")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(output_text)

