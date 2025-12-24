import sqlite3
import os

def add_manual_invoice(db_path="data/crm.db"):
    """
    Manually adds an invoice record to the CRM database.
    """
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Please run initialize_system.py first.")
        return

    print("--- Manual Invoice Entry ---")
    job_reference = input("Job Reference: ")
    customer_name = input("Customer Name: ")
    mbl_no = input("MBL No: ")
    hbl_no = input("HBL No: ")
    loading_port = input("Loading Port: ")
    discharge_port = input("Discharge Port: ")
    shipper = input("Shipper: ")
    consignee = input("Consignee: ")
    terms = input("Terms: ")
    due_date = input("Due Date: ")
    
    while True:
        try:
            total_amount = float(input("Total Amount: "))
            break
        except ValueError:
            print("Invalid amount. Please enter a number.")
            
    currency = input("Currency (default USD): ") or "USD"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO crm_invoices (job_reference, customer_name, mbl_no, hbl_no, loading_port, discharge_port, shipper, consignee, terms, due_date, total_amount, currency)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (job_reference, customer_name, mbl_no, hbl_no, loading_port, discharge_port, shipper, consignee, terms, due_date, total_amount, currency))
        
        conn.commit()
        print("Invoice added successfully!")
        
        # Option to add line items
        while True:
            add_item = input("Add a line item? (y/n): ").lower()
            if add_item != 'y':
                break
                
            desc = input("Description: ")
            while True:
                try:
                    amt = float(input("Amount: "))
                    break
                except ValueError:
                    print("Invalid amount.")
            
            cursor.execute('''
            INSERT INTO crm_line_items (job_reference, internal_code, description, amount)
            VALUES (?, ?, ?, ?)
            ''', (job_reference, "MANUAL", desc, amt))
            conn.commit()
            print("Line item added.")

    except Exception as e:
        print(f"Error adding data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Ensure we are in the project root or adjust path
    # Assuming script is run from project root or scripts folder
    
    # Check if data folder is in current dir or parent
    if os.path.exists("data/crm.db"):
        db_path = "data/crm.db"
    elif os.path.exists("../data/crm.db"):
        db_path = "../data/crm.db"
    else:
        # Default to project root assumption if running from root
        db_path = "data/crm.db"
        
    add_manual_invoice(db_path)
