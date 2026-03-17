import sqlite3
import glob

def find_database():
    db_files = glob.glob("*.db") + glob.glob("*.sqlite")
    for name in ["app.db", "database.db", "skillmatrix.db", "sql_app.db"]:
        if name in db_files: return name
    return db_files[0] if db_files else None

def update_global_experience_only():
    db_file = find_database()
    if not db_file: 
        print("❌ No database found.")
        return
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # We define the "Fair" Career mapping here.
        # These numbers are HIGHER than what is in your skills table.
        career_mapping = {
            5: 7,  # Expert gets 7 years total
            4: 5,  # Advanced gets 5 years total
            3: 3,  # Intermediate gets 3 years total
            2: 2,  # Basic gets 2 years total
            1: 1,  # Beginner gets 1 year total
            0: 0
        }

        print("🔄 Calculating higher global experience based on peak proficiency...")
        
        # Get the highest proficiency level for every developer
        cursor.execute("""
            SELECT developer_id, MAX(proficiency_level) 
            FROM developer_skills 
            GROUP BY developer_id
        """)
        dev_peaks = cursor.fetchall()
        
        updates = 0
        for dev_id, max_prof in dev_peaks:
            # Determine the fair global years based on the mapping
            global_years = career_mapping.get(max_prof or 0, 0)
            
            # Update ONLY the developers table
            cursor.execute(
                "UPDATE developers SET years_of_experience = ? WHERE id = ?", 
                (global_years, dev_id)
            )
            updates += 1

        conn.commit()
        print(f"✅ SUCCESS: Updated {updates} developers in the main table.")
        print("ℹ️ Note: developer_skills table remains UNTOUCHED.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_global_experience_only()