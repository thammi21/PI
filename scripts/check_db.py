import sqlite3

conn = sqlite3.connect("data/crm.db")
cursor = conn.cursor()

print("--- Invoices (ID, JobRef, Customer, MBL, HBL, LoadPort, DischPort, Amount, Currency) ---")
cursor.execute("SELECT id, job_reference, customer_name, mbl_no, hbl_no, loading_port, discharge_port, total_amount, currency FROM crm_invoices")
for row in cursor.fetchall():
    print(row)

print("\n--- Line Items ---")
cursor.execute("SELECT * FROM crm_line_items")
for row in cursor.fetchall():
    print(row)

conn.close()
