import sqlite3
import glob
import time
import sys

# Elegant, minimal color theme
BORDER_COLOR = '\033[96m'  # Cyan for the box
TEXT_COLOR = '\033[97m'    # Bright White for the text
RESET = '\033[0m'

def find_database():
    """Auto-detects the SQLite database file in the current folder."""
    db_files = glob.glob("*.db") + glob.glob("*.sqlite")
    for name in ["app.db", "database.db", "skillmatrix.db", "sql_app.db"]:
        if name in db_files: return name
    return db_files[0] if db_files else None

def get_unique_skills():
    db_file = find_database()
    
    if not db_file:
        return # Silently exit if no DB is found

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Query: Get ONLY the unique skill names, sorted alphabetically
        cursor.execute("SELECT DISTINCT skill_name FROM skills ORDER BY skill_name ASC")
        
        # Extract and format the names into a clean list
        skills = [str(row[0]).title() for row in cursor.fetchall()]
        
        if not skills:
            print("No skills found in the database.")
            return

        # Calculate the perfect box width based on your longest skill
        max_length = max(len(skill) for skill in skills)
        box_width = max_length + 4  # Adds 2 spaces of padding on left and right
        
        print("\n") # Add a little breathing room at the top

        # 1. Draw the top of the rounded box
        top_border = f"{BORDER_COLOR}╭" + "─" * box_width + f"╮{RESET}"
        sys.stdout.write(top_border + "\n")
        sys.stdout.flush()
        time.sleep(0.1) # Brief pause before the cascade starts

        # 2. Animate the skills cascading downwards
        for skill in skills:
            # Left-align the text with perfect padding
            padded_skill = f"  {skill.ljust(max_length)}  "
            
            # Construct the line with colored borders and white text
            line = f"{BORDER_COLOR}│{RESET}{TEXT_COLOR}{padded_skill}{RESET}{BORDER_COLOR}│{RESET}"
            
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
            time.sleep(0.04) # The "Animation" speed (0.04 seconds per line)

        # 3. Draw the bottom of the rounded box
        bottom_border = f"{BORDER_COLOR}╰" + "─" * box_width + f"╯{RESET}"
        sys.stdout.write(bottom_border + "\n\n")
        sys.stdout.flush()

    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
    finally:
        conn.close()

if __name__ == "__main__":
    get_unique_skills()