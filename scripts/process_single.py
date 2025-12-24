import os
import sqlite3
import logging
from src.extractor_azure import extract_invoice_data_llm
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_single():
    pdf_path = "data/sample_invoices/4 Skyfer.PDF"
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        return

    logger.info(f"Processing {pdf_path}...")
    try:
        # Temporarily modify extractor or just inspect here if possible.
        # Since we can't easily modify the return type of extract_invoice_data without breaking things,
        # let's just run the extraction and see the result.
        # To see KV pairs, we might need to modify extractor.py to log them.
        
        data = extract_invoice_data_llm(pdf_path)
        logger.info(f"Extracted: {data}")
        
        conn = sqlite3.connect("data/crm.db")
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO crm_invoices (job_reference, customer_name, total_amount, currency)
        VALUES (?, ?, ?, ?)
        ''', (data.job_reference, data.customer_name, data.total_amount, data.currency))
        
        for item in data.items:
            cursor.execute('''
            INSERT INTO crm_line_items (job_reference, internal_code, description, amount)
            VALUES (?, ?, ?, ?)
            ''', (data.job_reference, "N/A", item.description, item.amount))
            
        conn.commit()
        conn.close()
        logger.info("Successfully processed single invoice.")
        
    except Exception as e:
        logger.error(f"Failed: {e}")

if __name__ == "__main__":
    process_single()
