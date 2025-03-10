import json
import sqlite3
import zmq

def init_db():
    conn = sqlite3.connect("employee_sys.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            f_name TEXT NOT NULL,
            l_name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paychecks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            hours INTEGER NOT NULL,
            pay REAL NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id) on DELETE CASCADE 
        )
    """)
    conn.commit()
    conn.close()