import sqlite3
import pandas as pd
import os
from tabulate import tabulate

class StudentSystem:
    def __init__(self, db_name="university_records.db"):
        try:
            self.conn = sqlite3.connect(db_name)
            self.setup_database()
            print(f"Connected to: {db_name}")
        except Exception as e:
            print(f"Database Error: {e}")

    def setup_database(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # 1. Students Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                            sid INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            enroll_number TEXT UNIQUE NOT NULL)''')
        
        # 2. Courses Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
                            cid INTEGER PRIMARY KEY AUTOINCREMENT,
                            course_name TEXT NOT NULL UNIQUE)''')

        # 3. Enrollments Table (Linking Students to Courses)
        cursor.execute('''CREATE TABLE IF NOT EXISTS enrollments (
                            sid INTEGER,
                            cid INTEGER,
                            FOREIGN KEY(sid) REFERENCES students(sid) ON DELETE CASCADE,
                            FOREIGN KEY(cid) REFERENCES courses(cid) ON DELETE CASCADE)''')
        
        # 4. Performance Table (Marks)
        cursor.execute('''CREATE TABLE IF NOT EXISTS performance (
                            sid INTEGER,
                            marks REAL,
                            FOREIGN KEY(sid) REFERENCES students(sid) ON DELETE CASCADE)''')
        self.conn.commit()

    def enroll_student_in_course(self, enroll_num, course_name):
        """Logic to link a student to a specific course name."""
        cursor = self.conn.cursor()
        
        # Ensure course exists, if not, create it
        cursor.execute("INSERT OR IGNORE INTO courses (course_name) VALUES (?)", (course_name,))
        
        # Get IDs
        cursor.execute("SELECT sid FROM students WHERE enroll_number = ?", (enroll_num,))
        s_res = cursor.fetchone()
        cursor.execute("SELECT cid FROM courses WHERE course_name = ?", (course_name,))
        c_res = cursor.fetchone()

        if s_res and c_res:
            cursor.execute("INSERT INTO enrollments (sid, cid) VALUES (?, ?)", (s_res[0], c_res[0]))
            self.conn.commit()
            print(f"Enrolled successfully in {course_name}.")
        else:
            print("Error: Student not found.")

    def fetch_comprehensive_data(self, search_term=None):
        """
        Triple Join Logic:
        Joins Students + Performance + Enrollments + Courses
        """
        query = '''
            SELECT s.sid, s.name, s.enroll_number, c.course_name, p.marks 
            FROM students s 
            LEFT JOIN performance p ON s.sid = p.sid
            LEFT JOIN enrollments e ON s.sid = e.sid
            LEFT JOIN courses c ON e.cid = c.cid
        '''
        
        if search_term:
            query += " WHERE s.name LIKE ? OR s.enroll_number LIKE ? OR c.course_name LIKE ?"
            wildcard = f"%{search_term}%"
            df = pd.read_sql_query(query, self.conn, params=(wildcard, wildcard, wildcard))
        else:
            df = pd.read_sql_query(query, self.conn)

        if not df.empty:
            print("\n" + tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        else:
            print("No matching records found.")

    def add_new_entry(self, name, enroll, marks, course):
        """Full entry: Adds student, marks, and course enrollment in one go."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO students (name, enroll_number) VALUES (?, ?)", (name, enroll))
            sid = cursor.lastrowid
            cursor.execute("INSERT INTO performance (sid, marks) VALUES (?, ?)", (sid, marks))
            self.conn.commit()
            self.enroll_student_in_course(enroll, course)
        except sqlite3.IntegrityError:
            print("Error: Enrollment number already exists.")

# --- Operator Interface ---
def main():
    sys = StudentSystem()
    while True:
        print("\n[1] View All Records (Full Details)")
        print("[2] Search (Name/Enroll/Course)")
        print("[3] Add New Student & Enroll")
        print("[4] Enroll Existing Student in New Course")
        print("[5] Exit")
        
        choice = input("\nAction >> ")
        
        if choice == '1':
            sys.fetch_comprehensive_data()
        elif choice == '2':
            sys.fetch_comprehensive_data(input("Enter Keyword: "))
        elif choice == '3':
            sys.add_new_entry(input("Name: "), input("Enroll: "), float(input("Marks: ")), input("Course Name: "))
        elif choice == '4':
            sys.enroll_student_in_course(input("Enroll No: "), input("Course Name: "))
        elif choice == '5':
            break

if __name__ == "__main__":
    main()