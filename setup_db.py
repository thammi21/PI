import sqlite3
import os

def setup_database():
    db_path = "data/crm.db"
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crm_invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT UNIQUE,
        invoice_date TEXT,
        customer_name TEXT,
        total_amount REAL,
        currency TEXT DEFAULT 'USD'
    )
    ''')
    
    # Insert sample data
    # We will create a sample record that we will try to match against
    sample_data = [
        ('INV-2023-001', '2023-10-25', 'Acme Corp', 1500.00, 'USD'),
        ('INV-2023-002', '2023-10-26', 'Globex Corporation', 2500.50, 'USD'),
        ('INV-2023-003', '2023-11-01', 'Soylent Corp', 999.99, 'USD')
    ]
    
    try:
        cursor.executemany('''
        INSERT OR IGNORE INTO crm_invoices (invoice_number, invoice_date, customer_name, total_amount, currency)
        VALUES (?, ?, ?, ?, ?)
        ''', sample_data)
        conn.commit()
        print(f"Database initialized at {db_path} with sample data.")
    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    setup_database()
