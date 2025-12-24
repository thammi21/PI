import requests
import os

url = "http://127.0.0.1:8000/match"
file_path = "data/sample_invoice.pdf"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

with open(file_path, "rb") as f:
    files = {"file": f}
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(response.json())
    except Exception as e:
        print(f"Request failed: {e}")
