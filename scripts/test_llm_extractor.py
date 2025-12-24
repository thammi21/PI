import sys
import os
import json
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extractor_azure import extract_invoice_data_llm

import argparse

def test_extractor():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Test LLM Invoice Extractor")
    parser.add_argument("pdf_path", nargs="?", help="Path to the PDF file to extract", default=r"C:\Users\Thameem\Desktop\Thammi\Zybo\invoice-matcher-service\PI\data\sample_invoices\3 A2S Logistics.pdf")
    args = parser.parse_args()
    
    pdf_path = args.pdf_path
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print(f"Testing LLM Extractor on {pdf_path}...")
    try:
        data = extract_invoice_data_llm(pdf_path)
        print("\n--- Extracted Data ---")
        print(data.model_dump_json(indent=2))
        
        # Basic assertions
        # Basic assertions
        if data.supplier_inv_no and data.job_no:
            print(f"\nSUCCESS: Invoice No ({data.supplier_inv_no}) and Job No ({data.job_no}) extracted.")
            if data.supplier_inv_no == data.job_no:
                 print("\nWARNING: Invoice No and Job No are IDENTICAL. Detailed check required.")
            else:
                 print("\nSUCCESS: Invoice No and Job No are distinct.")
        else:
            print("\nWARNING: Invoice No or Job No missing.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_extractor()
