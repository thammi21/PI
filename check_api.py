import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("GOOGLE_API_KEY not found.")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("Available Models:")
        for model in data.get('models', []):
            print(f"- {model['name']}")
            if 'gemini' in model['name']:
                print(f"  Supported methods: {model.get('supportedGenerationMethods')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Request failed: {e}")
