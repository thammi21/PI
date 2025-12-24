import sqlite3
import os

db_path = r"data/crm.db"

def update_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Add missing columns to crm_invoices
    columns_to_add = [
        ("supplier", "TEXT"),
        ("supplier_inv_no", "TEXT"),
        ("supplier_inv_date", "TEXT")
    ]
    
    # Get current columns
    cursor.execute("PRAGMA table_info(crm_invoices)")
    current_columns = [row[1] for row in cursor.fetchall()]

    for col_name, col_type in columns_to_add:
        if col_name not in current_columns:
            print(f"Adding column {col_name} to crm_invoices...")
            try:
                cursor.execute(f"ALTER TABLE crm_invoices ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Error adding column {col_name}: {e}")

    # 2. Ensure crm_line_items exists
    # Using schema from initialize_system.py
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
    
    # 3. Upsert Invoice Data (ID = 6)
    invoice_data = {
        "id": 6,
        "supplier": "SEACALL logistics",
        "supplier_inv_no": "FV/25/06/00372",
        "supplier_inv_date": "2025-06-11",
        "job_no": "SEACALL/E/25/05/0166", # Maps to job_reference
        "currency": "USD",
        "customer_name": "COMPASS SEA & AIR CARGO LLC",
        "due_date": None,
        # Defaulting other fields to None if they are needed for the INSERT but might be NULLABLE
        "total_amount": 0.0 # Will calculate from items? Or just leave as is/update? 
        # User didn't provide total_amount in the top level JSON but items have amounts. 
        # Sum of items: 3130 + 60 + 70 + 80 = 3340.
    }
    
    # Calculate total amount
    total_amount = sum(item['amount'] for item in [
        {"amount": 3130.0}, {"amount": 60.0}, {"amount": 70.0}, {"amount": 80.0}
    ])
    
    # Check if ID 6 exists
    cursor.execute("SELECT id FROM crm_invoices WHERE id = ?", (6,))
    exists = cursor.fetchone()
    
    if exists:
        print("Updating invoice ID 6...")
        cursor.execute("""
            UPDATE crm_invoices 
            SET supplier = ?, supplier_inv_no = ?, supplier_inv_date = ?, job_reference = ?, 
                currency = ?, customer_name = ?, due_date = ?, total_amount = ?
            WHERE id = ?
        """, (
            invoice_data["supplier"], invoice_data["supplier_inv_no"], invoice_data["supplier_inv_date"],
            invoice_data["job_no"], invoice_data["currency"], invoice_data["customer_name"],
            invoice_data["due_date"], total_amount, 6
        ))
    else:
        print("Inserting invoice ID 6...")
        # We need to be careful with columns. 
        # Insert with explicit ID.
        cursor.execute("""
            INSERT INTO crm_invoices 
            (id, supplier, supplier_inv_no, supplier_inv_date, job_reference, 
             currency, customer_name, due_date, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            6, invoice_data["supplier"], invoice_data["supplier_inv_no"], invoice_data["supplier_inv_date"],
            invoice_data["job_no"], invoice_data["currency"], invoice_data["customer_name"],
            invoice_data["due_date"], total_amount
        ))

    # 4. Handle Line Items
    job_ref = invoice_data["job_no"]
    
    # Clear existing items for this job_reference (to avoid duplication on re-run)
    cursor.execute("DELETE FROM crm_line_items WHERE job_reference = ?", (job_ref,))
    
    items = [
        {"description": "EXW Białołęka - CY Koper - CFR Alexandria", "amount": 3130.0},
        {"description": "Doc Fee", "amount": 60.0},
        {"description": "Customs clearance", "amount": 70.0},
        {"description": "VGM", "amount": 80.0}
    ]
    
    print(f"Inserting {len(items)} line items for job {job_ref}...")
    for item in items:
        cursor.execute("""
            INSERT INTO crm_line_items (job_reference, internal_code, description, amount)
            VALUES (?, ?, ?, ?)
        """, (job_ref, "N/A", item["description"], item["amount"]))

    conn.commit()
    conn.close()
    print("Database updated successfully.")

if __name__ == "__main__":
    update_db()
