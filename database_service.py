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


def database_server():
    init_db()
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5556")
    print("Database service running on port 5555....")

    while True:
        message = socket.recv_json()
        command = message.get("command")

        conn = sqlite3.connect("employee_sys.db")
        cursor = conn.cursor()

        try:
            if command == "add_employee":
                cursor.execute("INSERT INTO employees (f_name, l_name, phone, email) VALUES (?, ?, ?, ?)",
                               (message["first_name"], message["last_name"], message["phone"], message["email"]))
                conn.commit()
                response = {"status": "success", "message": "Employee added"}
                print("Added employee to database")
            elif command == "view_employees":
                cursor.execute("SELECT * FROM employees")
                response = {"status": "success", "data": cursor.fetchall()}
                print("Sending list of employees")
            elif command == "delete_employee":
                cursor.execute("DELETE FROM employees WHERE id = ?", (message["id"]))
                conn.commit()
                response = {"status": "success", "message": "Employee deleted"}
                print("Deleted employee from database")
            elif command == "update_employee":
                cursor.execute("UPDATE employees SET f_name = ?, l_name = ?, phone = ?, email = ? WHERE id = ?",
                               (message["first_name"], message["last_name"], message["phone"], message["email"], message["id"]))
                conn.commit()
                response = {"status": "success", "message": "Employee deleted"}
                print("Updated employee entry in database")
            elif command == "add_paycheck":
                cursor.execute("INSERT INTO paychecks (employee_id, hours, rate, pay) VALUES (?, ?, ?, ?)",
                               (message["employee_id"], message["hours"], message["rate"], message["pay"]))
                conn.commit()
                response = {"status": "success", "message": "Paycheck added"}
                print("Added paycheck to database")
            elif command == "view_paychecks":
                cursor.execute("SELECT * FROM paychecks WHERE ID = ?")
                response = {"status": "succuss", "data": cursor.fetchall()}
                print("Sending list of paychecks")
            elif command == "delete_paycheck":
                cursor.execute("DELETE FROM paychecks WHERE ID = ?", (message["id"]))
                conn.commit()
                response = {"status": "success", "message": "Paycheck deleted"}
                print("Deleted paycheck from database")
            elif command == "update_paycheck":
                cursor.execute("UPDATE paycheck SET employee_id = ?, hours = ?, rate = ?, pay = ? WHERE id = ?",
                               (message["employee_id"], message["hours"], message["rate"], message["pay"], message["id"]))
                conn.commit()
                response = {"status": "success", "message": "Paycheck deleted"}
                print("Updated paycheck entry in database")
            else:
                response = {"status": "error", "message": "Invalid command"}
                print("Error: invalid command")
        except Exception as e:
            response = {"status": "error", "message": str(e)}
            print("Error: Exception")

        conn.close()
        socket.send_json(response)

if __name__ == "__main__":
    database_server()
