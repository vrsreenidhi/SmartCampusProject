import sqlite3

def connect_db():
    conn = sqlite3.connect("database/campus.db")
    return conn

def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        score REAL,
        grade TEXT,
        remark TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        course_name TEXT,
        credits INTEGER
    )
    """)

    conn.commit()
    conn.close()

create_tables()