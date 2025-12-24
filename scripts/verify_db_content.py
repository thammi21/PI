import sqlite3
import pandas as pd

def verify_db():
    conn = sqlite3.connect('data/crm.db')
    query = "SELECT job_reference, shipper, consignee FROM crm_invoices"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("Database Content Verification:")
    print(df)
    
    if df['shipper'].isnull().all() or df['consignee'].isnull().all():
        print("\nWARNING: Shipper or Consignee columns appear to be empty!")
    else:
        print("\nSUCCESS: Shipper and Consignee columns contain data.")

if __name__ == "__main__":
    verify_db()
