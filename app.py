from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from database_ops import *
from ml_ops import *
import uuid

available_models = load_new_model(available_models, "SickleCell")


app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Create a new person in the table and upload an associated image with it
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

    filename =  uuid.uuid4().hex + secure_filename(file.filename) 
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    db_create_person(name, age, blood_group, gender, file_path)

    return jsonify({'message': 'Image uploaded successfully', 'filename': filename}), 200


# Return a json object with all the values in the table
# Use this to implement the table in the dashboard
@app.route('/getall')
def getall():
    values = db_get_people()
    values = [{
        'id' : i[0],
        'name' : i[1],
        'age' : i[2],
        'bloodGroup' : i[3],
        'gender' : i[4],
        'img_path' : i[5]
        } for i in values]
    return jsonify(values)

# Get a single person based on ID
@app.route('/getone', methods=['POST'])
def getone():
    id = request.form.get('id')
    # return predict_img(db_get_person(2)[0][], model)
    data = list(db_get_person(id)[0])
    
    data = {"id" : data[0], "name" : data[1], "age" : data[2], "blood_group" : data[3], "gender" : data[4], "img_path" : data[5]}
    return jsonify(data)

# Delete a record in the table based on name, age, etc
@app.route('/delete', methods=['POST'])
def delete_records():
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    blood_group = request.form.get('blood_group')
    db_delete_person(name, age, blood_group, gender)

# Machine Learning Routes

# Return a list of available models and details
@app.route('/model_details')
def get_modeldetails():
    return jsonify(available_models)

# Run the model on a record and return the value
@app.route('/run_model', methods=['POST'])
def run_model():
    try:
        id = request.form.get('id')
        if not id:
            return jsonify({"error": "Patient ID is required"}), 400

        record = db_get_person(id)
        if not record:
            return jsonify({"error": "Patient not found"}), 404

        image_path = record[0][5]  # Assuming img_path is at index 5
        
        # Handle null/empty paths
        if not image_path or str(image_path).lower() == "null":
            return jsonify({"error": "No image associated with this patient"}), 400

        if not os.path.exists(image_path):
            return jsonify({"error": f"Image file not found at: {image_path}"}), 400

        output = predict_img(image_path, available_models["SickleCell"])
        return jsonify({"prediction": output})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Testing Routes
@app.route('/test')
def testshit():
    db_create_person("John Doe", 24, "O+", "Male", "Null")
    print(db_get_people())
    return "Testing..."

@app.route('/test1')
def test1():
    return "The app is running"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)