import sqlite3

# Database stuff

# Create table
with sqlite3.connect("people.db") as conn:
    cursor = conn.cursor()
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS people (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           name TEXT NOT NULL,
           age INTEGER NOT NULL,
           blood_group TEXT NOT NULL,
           gender TEXT NOT NULL,
           img_path TEXT NOT NULL
       );
    """)
# Functions to do stuff with the table

# Create a new person record
def db_create_person(name : str, age : int,
                  blood_group : str, gender : str,
                  img_path : str) -> None:
    with sqlite3.connect("people.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO people (name, age, blood_group, gender, img_path)
            VALUES(?, ?, ?, ?, ?);
        """, (name, age, blood_group, gender, img_path))
    return None

# Get all the people
def db_get_people() -> list:
    stuff = []
    with sqlite3.connect("people.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, blood_group, gender, img_path FROM PEOPLE;")
        stuff = cursor.fetchall()
    return stuff

def db_delete_person(
    name : str, age : int,
    blood_group : str, gender : str
    ) -> None:
    with sqlite3.connect("people.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM people WHERE name = ? AND age = ? AND blood_group = ? AND gender = ?",(name, age, blood_group, gender, img_path) )
        conn.commit()
    return None

def db_get_person(id : int) -> list:
    stuff = [] 
    with sqlite3.connect("people.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM people WHERE id = ?", (str(id),))
        stuff = cursor.fetchall()
    return stuff

