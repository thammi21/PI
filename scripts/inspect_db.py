import sqlite3
import json
import sys

# Force utf-8 for stdout if possible, or just handle errors manually
sys.stdout.reconfigure(encoding='utf-8')

db_path = r"data/crm.db"

def verify_update():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    # Check Invoice
    print("Checking Invoice ID 6:")
    cursor.execute("SELECT * FROM crm_invoices WHERE id = 6")
    row = cursor.fetchone()
    if row:
        # Convert to dict and print
        d = dict(row)
        print(d)
        job_ref = row['job_reference']
        
        # Check Items
        print(f"\nChecking Line Items for Job {job_ref}:")
        cursor.execute("SELECT * FROM crm_line_items WHERE job_reference = ?", (job_ref,))
        items = cursor.fetchall()
        for item in items:
            item_dict = dict(item)
            # manually replace problematic chars if reconfigure doesn't work (just in case)
            print(str(item_dict).encode('ascii', 'replace').decode('ascii')) 
    else:
        print("Invoice ID 6 not found!")

    conn.close()

if __name__ == "__main__":
    verify_update()
