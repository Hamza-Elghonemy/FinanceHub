import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

with open(r"data/prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

with open(r"data/combined_financial_data_yearly_ratios.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)

sector_choice = input("Enter sector (Tech or Healthcare): ").strip().capitalize()

if sector_choice not in all_data:
    raise ValueError(f"Sector '{sector_choice}' not found. Available: {list(all_data.keys())}")

sector_data = {sector_choice: all_data[sector_choice]}

sector_file = f"{sector_choice}_only.json"
with open(sector_file, "w", encoding="utf-8") as f:
    json.dump(sector_data, f, indent=2)

print(f"✅ Saved sector data to {sector_file}")

with open(sector_file, "r", encoding="utf-8") as f:
    sector_json = f.read()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": prompt},  
        {"role": "user", "content": sector_json} 
    ],
    temperature=0
)

output_text = response.choices[0].message.content

output_file = f"{sector_choice}_analysis.json"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(output_text)

print(f"✅ LLM analysis saved to {output_file}")