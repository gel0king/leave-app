import sqlite3
from flask import g
from utils.config import get_db_path

def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    if "db" not in g:
        db_path = get_db_path()

        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(exception=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

def init_db(db_path):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    #Create employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees ()
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_number INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            office TEXT,

            -- Leave is stored as 30 minute intervals
            starting_annual_leave INTEGER DEFAULT 0,
            starting_sick_leave INTEGER DEFAULT 0,

            start_date TEXT NOT NULL,
            employment_status TEXT,
            employment_date DATE,
            employment_history TEXT,
            probation_end_date DATE,

            departure_date DATE,
            return_date DATE,

            driver_license_state TEXT,
            license_number TEXT,
            driver_license_expire_date DATE,

            other_id TEXT,
            other_id_number TEXT,
            ssn INTEGER,
            date_of_birth DATE,

            insurance_expires DATE,

            address TEXT,
            city TEXT,
            state TEXT,
            zip INTEGER,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """)

    # Create leave_types table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            auto_accrual INTEGER DEFAULT 0,
        )
    """)

    # Create log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type_id INTEGER,
            action TEXT,
            description TEXT,
            old_values TEXT,
            new_values TEXT,
            notes TEXT,
            time_Created DATE,
            start_date DATE,
            end_date DATE,
            hours REAL,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            FOREIGN KEY (leave_type_id) REFERENCES leave_types(id) ON DELETE CASCADE
        )
    """)

    cur = cursor.execute("SELECT COUNT(*) FROM leave_types")
    if cur.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO leave_types (name, unit, auto_accrual) VALUES (?, ?, ?)",
            [
                ("Annual leave", "hours", 1),
                ("Sick leave", "hours", 1),
                ("Emergency leave", "hours", 0),
                ("Leave without pay", "hours", 0),
                ("Military leave", "hours", 0),
                ("Extended sick leave", "hours", 0),
                ("Jury Duty", "hours", 0),
                ("Holiday leave taken", "hours", 0),
                ("Other", "hours", 0),
            ],
        )

