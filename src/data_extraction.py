import json
import requests


company_symbols = ["JNJ", "PFE","ABT","CVS","UNH", "META"]
financial_statements = ["BALANCE_SHEET", "INCOME_STATEMENT", "CASH_FLOW","OVERVIEW"]

for company_symbol in company_symbols:
    for statement in financial_statements:
        url = f'https://www.alphavantage.co/query?function={statement}&symbol={company_symbol}&apikey=1M7X2X1CUZNAYNDA'
        r = requests.get(url)
        data = r.json()
        # save to a json file
        with open(f'{company_symbol}_{statement}.json', 'w') as f:
            json.dump(data, f, indent=2)