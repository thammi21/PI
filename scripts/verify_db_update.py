import sqlite3
import pandas as pd

def verify_db():
    conn = sqlite3.connect("data/crm.db")
    try:
        df = pd.read_sql_query("SELECT * FROM crm_invoices", conn)
        print(df.head())
        print("\nColumns:", df.columns.tolist())
        
        if 'shipper' in df.columns and 'consignee' in df.columns:
            print("\nSUCCESS: 'shipper' and 'consignee' columns exist.")
            print(f"Shipper values found: {len(df['shipper'].unique())}")
            print(f"Consignee values found: {len(df['consignee'].unique())}")
            # print("Shipper values:\n", [str(x).encode('utf-8', errors='ignore').decode('utf-8') for x in df['shipper'].unique()])
            # print("Consignee values:\n", [str(x).encode('utf-8', errors='ignore').decode('utf-8') for x in df['consignee'].unique()])
        else:
            print("\nFAILURE: Missing columns.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_db()
