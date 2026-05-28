import os
import sqlite3

# Force the script to look in its exact folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'students.db')

print("Fetching Epic Arena Results...\n")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scores")
    results = cursor.fetchall()
    
    if len(results) == 0:
        print("Table exists, but no scores yet. Run the quiz!")
    else:
        # 1. Print the headers perfectly aligned
        print(f"{'St_Name':<15} {'Score':<10} {'Time'}")
        print("-" * 35) # Creates a clean dividing line
        
        # 2. Print each student 1 by 1 under the headers
        for row in results:
            name = str(row[0])
            score = f"{row[1]}/20"
            
            # 3. Extract just the Hour and Minute from "YYYY-MM-DD HH:MM:SS"
            raw_time = str(row[2])
            try:
                # Splits by space to drop the date, then keeps only the first 5 characters (HH:MM)
                time_only = raw_time.split(" ")[1][:5]
            except:
                time_only = raw_time # Fallback just in case
                
            # Print the row with exact spacing to match the headers
            print(f"{name:<15} {score:<10} {time_only}")
            
    conn.close()
except Exception as e:
    print("\nERROR: Could not read scores table.", e)
