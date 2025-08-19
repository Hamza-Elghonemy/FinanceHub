import os
import tiktoken

# Path to your JSON file
file_path = "financials_cleaned.json"

# Read file
with open(file_path, "r", encoding="utf-8") as f:
    data = f.read()

# File size in KB
file_size_kb = os.path.getsize(file_path) / 1024

# Choose encoding for GPT-4o / GPT-4.1 / GPT-4o-mini
encoding = tiktoken.encoding_for_model("gpt-4o-mini")

# Count tokens
token_count = len(encoding.encode(data))

# Print results
print(f"File: {file_path}")
print(f"Size: {file_size_kb:.2f} KB")
print(f"Token count: {token_count}")
