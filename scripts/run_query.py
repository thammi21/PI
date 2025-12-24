import sqlite3

# Configuration
db_path = "data/crm.db"

def update_customers():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # --- UPDATE COMMANDS ---
        # Update ID 1
        new_name_1 = "COMPASS OCEAN LOGISTICS"
        cursor.execute("UPDATE crm_invoices SET customer_name = ? WHERE id = ?", (new_name_1, 1))

        # Update ID 8
        new_name_8 = "COMPASS OCEAN LOGISTICS"
        cursor.execute("UPDATE crm_invoices SET customer_name = ? WHERE id = ?", (new_name_8, 8))
        
        # Check if rows were actually found and updated
        if cursor.rowcount == 0:
            print("No rows updated. Are you sure IDs 1 and 8 exist?")
        else:
            conn.commit() # <--- Important! Saves the changes
            print("Update successful!")

        # --- VERIFICATION ---
        print("\n--- Verifying Changes ---")
        cursor.execute("SELECT id, customer_name FROM crm_invoices WHERE id IN (1, 8)")
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row[0]} | Name: {row[1]}")

    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_customers()