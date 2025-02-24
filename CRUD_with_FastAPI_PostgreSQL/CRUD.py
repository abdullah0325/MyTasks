from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
loaqd_dotenv()
import os

DB_url= os.getenv("DB_url")

app = FastAPI()

# Database connection
def get_db_connection():  # This function is used to connect to the database
    return psycopg2.connect(    # this  line is used to connect to the database
        DB_url,
        cursor_factory=RealDictCursor 
    )

# Create table if it doesn't exist
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            id_card_no VARCHAR(100) UNIQUE,
            salary INTEGER
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# Create the table when the app starts
create_table()

@app.post("/create/")
def create_employee(id: int, name: str, id_card_no: str, salary: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if employee exists
    cur.execute("SELECT id FROM employees WHERE id = %s", (id,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return {"message": "Employee already exists"}
    
    # Create new employee
    cur.execute(
        "INSERT INTO employees (id, name, id_card_no, salary) VALUES (%s, %s, %s, %s)",
        (id, name, id_card_no, salary)
    )
    conn.commit()
    
    # Get the created employee
    cur.execute("SELECT * FROM employees WHERE id = %s", (id,))
    new_employee = cur.fetchone()
    
    cur.close()
    conn.close()
    return "the new employee added", dict(new_employee)

@app.get("/read/")
def get_employee(id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM employees WHERE id = %s", (id,))
    employee = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if employee:
        return dict(employee)
    return {"message": "Employee not found"}

@app.put("/update/")
def update_employee(id: int, salary: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE employees SET salary = %s WHERE id = %s RETURNING *",
        (salary, id)
    )
    updated_employee = cur.fetchone()
    conn.commit()
    
    cur.close()
    conn.close()
    
    if updated_employee:
        return dict(updated_employee)
    return {"message": "Employee not found"}

@app.delete("/delete/")
def delete_employee(id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM employees WHERE id = %s RETURNING id", (id,))
    deleted = cur.fetchone()
    conn.commit()
    
    cur.close()
    conn.close()
    
    if deleted:
        return {"message": "Employee deleted successfully"}
    return {"message": "Employee not found"}

