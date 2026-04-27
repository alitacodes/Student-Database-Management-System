import sqlite3
import pandas as pd
import os
from tabulate import tabulate

class StudentSystem:
    def __init__(self, db_name="student_records.db"):
        # No complex connection string needed
        try:
            self.conn = sqlite3.connect(db_name)
            self.setup_database()
            print(f"Connected to local database: {db_name}")
        except Exception as e:
            print(f"Database Error: {e}")

    def setup_database(self):
        cursor = self.conn.cursor()
        # Enable Foreign Key support in SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Table 1: Students
        cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                            sid INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            enroll_number TEXT UNIQUE NOT NULL)''')
        
        # Table 2: Courses
        cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
                            cid INTEGER PRIMARY KEY AUTOINCREMENT,
                            course_name TEXT NOT NULL)''')

        # Table 3: Enrollments (Mapping table)
        cursor.execute('''CREATE TABLE IF NOT EXISTS enrollments (
                            sid INTEGER,
                            cid INTEGER,
                            FOREIGN KEY(sid) REFERENCES students(sid))''')

        # Table 4: Performance (Marks table)
        cursor.execute('''CREATE TABLE IF NOT EXISTS performance (
                            sid INTEGER,
                            marks REAL,
                            FOREIGN KEY(sid) REFERENCES students(sid))''')
        self.conn.commit()

    def import_from_file(self, file_path):
        """Buffer logic: Read -> Check Relevance -> Insert"""
        if not os.path.exists(file_path):
            print("File not found!")
            return

        try:
            ext = os.path.splitext(file_path)[1].lower()
            df = pd.read_csv(file_path) if ext == '.csv' else pd.read_excel(file_path)

            # Relevance Check
            required = {'name', 'enroll_number', 'marks'}
            if not required.issubset(df.columns):
                print(f"Irrelevant file! Missing headers: {required - set(df.columns)}")
                return

            cursor = self.conn.cursor()
            for _, row in df.dropna(subset=['name', 'enroll_number']).iterrows():
                try:
                    # Insert Student
                    cursor.execute("INSERT INTO students (name, enroll_number) VALUES (?, ?)", 
                                   (row['name'], str(row['enroll_number'])))
                    new_sid = cursor.lastrowid # Get the generated sid
                    
                    # Insert Marks into 4th table
                    cursor.execute("INSERT INTO performance (sid, marks) VALUES (?, ?)", 
                                   (new_sid, row['marks']))
                except sqlite3.IntegrityError:
                    continue # Skip duplicates
            
            self.conn.commit()
            print(f"Successfully processed {len(df)} rows.")

        except Exception as e:
            print(f"Processing Error: {e}")

    def display_all(self):
        query = '''
            SELECT s.sid, s.name, s.enroll_number, p.marks 
            FROM students s
            LEFT JOIN performance p ON s.sid = p.sid
        '''
        try:
            df = pd.read_sql_query(query, self.conn)
            if df.empty:
                print("\nNo records found.")
            else:
                print("\n" + tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        except Exception as e:
            print(f"Display Error: {e}")

# --- Main Program ---
if __name__ == "__main__":
    app = StudentSystem()
    
    while True:
        print("\n--- Student Database Management (SQLite) ---")
        print("1. View All Records")
        print("2. Import CSV/Excel")
        print("3. Exit")
        
        choice = input("Select: ")
        if choice == '1':
            app.display_all()
        elif choice == '2':
            path = input("Enter file path: ").strip('"')
            app.import_from_file(path)
        elif choice == '3':
            app.conn.close()
            print("Database connection closed.")
            break