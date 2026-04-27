# Student Database Management System

This project is a simple Student Database Management System built with Python and SQLite. It allows you to manage student records, import data from CSV/Excel files, and display all records in a tabular format.

## Features
- Store student information (name, enrollment number, marks)
- Import student data from CSV or Excel files
- View all student records in a formatted table
- Uses SQLite as the backend database
- Command-line interface for easy interaction

## Requirements
- Python 3.12+
- pandas
- tabulate
- openpyxl (for Excel file support)

All dependencies can be installed using pip:

```
pip install pandas tabulate openpyxl
```

## Usage
1. Clone the repository or download the code.
2. (Optional) Create and activate a virtual environment:
   ```
   python -m venv myenv
   myenv\Scripts\activate  # On Windows
   source myenv/bin/activate  # On Linux/Mac
   ```
3. Install dependencies as shown above.
4. Run the main program:
   ```
   python sms.py
   ```
5. Follow the on-screen menu to:
   - View all records
   - Import data from a CSV or Excel file
   - Exit the program

## File Structure
- `sms.py` : Main application file containing the StudentSystem class and CLI
- `myenv/` : (Optional) Virtual environment directory

## Notes
- The database file (`student_records.db`) will be created in the project directory.
- Imported files must contain the columns: `name`, `enroll_number`, and `marks`.
- Duplicate student entries (by enrollment number) are skipped during import.

## License
This project is for educational purposes.
