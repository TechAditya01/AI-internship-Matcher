import sqlite3

def print_internships_columns(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(internships);")
    columns = cursor.fetchall()
    print("Columns in internships table:")
    for col in columns:
        print(col)

if __name__ == "__main__":
    print_internships_columns('instance/internship_matching.db')
