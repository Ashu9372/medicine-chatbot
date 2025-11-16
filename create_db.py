# File: create_db.py
import pandas as pd
import sqlite3
import sys

CSV_FILE = "data.csv"
DB_FILE = "medicines.db"
TABLE_NAME = "medicines" # This will be the name of the table inside your database

try:
    df = pd.read_csv(CSV_FILE)
    conn = sqlite3.connect(DB_FILE)
    
    # This command saves your DataFrame into the database file
    # if_exists="replace" means you can run this script again if you update your CSV
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    
    conn.close()
    print(f"✅ Success! Your '{CSV_FILE}' data is now in '{DB_FILE}'.")

except FileNotFoundError:
    print(f"❌ ERROR: '{CSV_FILE}' not found. Make sure it's in the same folder.")
    sys.exit(1)
except Exception as e:
    print(f"❌ An error occurred: {e}")
    sys.exit(1)