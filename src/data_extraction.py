import finnhub
import json

finnhub_client = finnhub.Client(api_key="d2g70k9r01qkv5ng29kgd2g70k9r01qkv5ng29l0")

fin = finnhub_client.financials_reported(symbol="AAPL", freq="quarterly")

with open('financials_reported.json', 'w') as f:
    json.dump(fin, f, indent=2)
