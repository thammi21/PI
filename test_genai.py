import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("GOOGLE_API_KEY not found.")
else:
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello, are you working?")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-1.5-flash: {e}")
        
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-001")
        response = model.generate_content("Hello, are you working?")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-1.5-flash-001: {e}")

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content("Hello, are you working?")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-pro: {e}")
