import os
import sys
import sqlite3
import logging
import time
from dotenv import load_dotenv

# Add parent directory to path to import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extractor_azure import extract_invoice_data_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SystemInitializer")

def setup_database(db_path="data/crm.db"):
    """Creates the database schema."""
    if os.path.exists(db_path):
        logger.info(f"Removing existing database: {db_path}")
        os.remove(db_path)
        
    logger.info(f"Creating new database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Invoices Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crm_invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_reference TEXT,
        customer_name TEXT,
        mbl_no TEXT,
        hbl_no TEXT,
        container_no TEXT,
        container_type TEXT,
        loading_port TEXT,
        discharge_port TEXT,
        shipper TEXT,
        consignee TEXT,
        terms TEXT,
        due_date TEXT,
        total_amount REAL,
        currency TEXT DEFAULT 'USD'
    )
    ''')
    
    # Create Line Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crm_line_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_reference TEXT,
        internal_code TEXT,
        description TEXT,
        amount REAL,
        FOREIGN KEY (job_reference) REFERENCES crm_invoices (job_reference)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database schema created successfully.")

def process_invoices(sample_dir="data/sample_invoices", db_path="data/crm.db"):
    """Processes all PDFs in the sample directory and populates the DB."""
    if not os.path.exists(sample_dir):
        logger.error(f"Directory not found: {sample_dir}")
        return

    pdf_files = [f for f in os.listdir(sample_dir) if f.lower().endswith('.pdf')]
    total_files = len(pdf_files)
    logger.info(f"Found {total_files} PDFs to process in {sample_dir}.")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for i, pdf_file in enumerate(pdf_files):
        pdf_path = os.path.join(sample_dir, pdf_file)
        logger.info(f"Processing {i+1}/{total_files}: {pdf_file}...")
        
        try:
            # Extract Data
            data = extract_invoice_data_llm(pdf_path)
            
            # Insert Invoice
            cursor.execute('''
            INSERT INTO crm_invoices (job_reference, customer_name, mbl_no, hbl_no, container_no, container_type, loading_port, discharge_port, shipper, consignee, terms, due_date, total_amount, currency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data.job_reference, data.customer_name, data.mbl_no, data.hbl_no, data.container_no, data.container_type, data.loading_port, data.discharge_port, data.shipper, data.consignee, data.terms, data.due_date, data.total_amount, data.currency))
            
            # Insert Line Items
            for item in data.items:
                cursor.execute('''
                INSERT INTO crm_line_items (job_reference, internal_code, description, amount)
                VALUES (?, ?, ?, ?)
                ''', (data.job_reference, "N/A", item.description, item.amount))
            
            conn.commit()
            logger.info(f"Successfully processed {pdf_file}")
            
            # Add delay to avoid Rate Limit (429)
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file}: {e}")
            
    conn.close()
    logger.info("Batch processing complete.")

def main():
    load_dotenv()
    setup_database()
    process_invoices()

if __name__ == "__main__":
    main()
