from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
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

# Get all the people
def db_get_people() -> list:
    stuff = []
    with sqlite3.connect("people.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, age, blood_group, gender, img_path FROM PEOPLE;")
        stuff = cursor.fetchall()
    return stuff









app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Get the other data and stuff
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    blood_group = request.form.get('blood_group')

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    db_create_person(name, age, blood_group, gender, file_path)

    return jsonify({'message': 'Image uploaded successfully', 'filename': filename}), 200


@app.route('/test')
def testshit():
    db_create_person("John Doe", 24, "O+", "Male", "Null")
    print(db_get_people())
    return "Testing..."


if __name__ == '__main__':
    app.run(debug=True)

