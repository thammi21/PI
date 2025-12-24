import sys
import os
from dotenv import load_dotenv
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extractor_azure import extract_invoice_data_llm

def verify_extraction(pdf_path):
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print(f"Extracting from: {pdf_path}")
    try:
        data = extract_invoice_data_llm(pdf_path)
        print("\n--- Extracted Data ---")
        print(f"Job Reference: {data.job_reference}")
        print(f"Container No: {data.container_no}")
        print(f"Container Type: {data.container_type}")
        print(f"Customer: {data.customer_name}")
        print("-" * 20)
        print(data.model_dump_json(indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    pdf_path = r"data/sample_invoices/3 A2S Logistics.pdf"
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    verify_extraction(pdf_path)
