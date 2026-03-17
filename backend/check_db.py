import sqlite3
import pandas as pd
import glob
import os

def find_database():
    """Auto-detects the SQLite database file in the current folder."""
    db_files = glob.glob("*.db") + glob.glob("*.sqlite")
    if not db_files:
        return None
    
    # Prioritize common FastAPI database names
    for common_name in ["app.db", "database.db", "skillmatrix.db", "sql_app.db"]:
        if common_name in db_files:
            return common_name
            
    return db_files[0] # Return the first one found if no common names match

def inspect_database():
    db_file = find_database()
    
    if not db_file:
        print("❌ ERROR: Could not find any SQLite database (.db) files in this directory.")
        print("Make sure you are running this script from your 'backend' folder.")
        return

    print(f"✅ Connected to database: {db_file}")
    conn = sqlite3.connect(db_file)
    
    try:
        # Fetch a list of all tables in the database
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        tables = pd.read_sql_query(tables_query, conn)['name'].tolist()
        
        print(f"📂 Found Tables: {', '.join(tables)}\n")

        # Print the first 5 rows of every table
        for table in tables:
            print(f"--- 📊 TABLE: {table.upper()} ---")
            df = pd.read_sql_query(f"SELECT * FROM {table};", conn)
            
            print(f"Total Rows: {len(df)}")
            
            if len(df) > 0:
                print(df.head(5).to_string(index=False)) # Prints a clean, formatted table
            else:
                print("⚠️ WARNING: This table is completely EMPTY.")
            print("\n" + "="*50 + "\n")

    except Exception as e:
        print(f"❌ Error reading database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting Database Inspector...")
    inspect_database()