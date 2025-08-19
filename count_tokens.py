import os
import tiktoken

file_path = "financials_cleaned.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = f.read()

file_size_kb = os.path.getsize(file_path) / 1024

encoding = tiktoken.encoding_for_model("gpt-4o-mini")

token_count = len(encoding.encode(data))

print(f"File: {file_path}")
print(f"Size: {file_size_kb:.2f} KB")
print(f"Token count: {token_count}")
