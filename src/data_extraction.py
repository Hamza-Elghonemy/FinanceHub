import json
import requests


company_symbols = ["JNJ", "PFE","ABT","CVS","UNH"]
financial_statements = ["BALANCE_SHEET", "INCOME_STATEMENT", "CASH_FLOW","OVERVIEW"]

for company_symbol in company_symbols:
    for statement in financial_statements:
        url = f'https://www.alphavantage.co/query?function={statement}&symbol={company_symbol}&apikey=1XNOZA5CSL7306MI'
        r = requests.get(url)
        data = r.json()
        # save to a json file
        with open(f'{company_symbol}_{statement}.json', 'w') as f:
            json.dump(data, f, indent=2)