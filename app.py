from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_image():
    print("Image upload tried")
    if 'image' not in request.files:
        print("No image part")
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']
    if file.filename == '':
        print("no filename")
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    return jsonify({'message': 'Image uploaded successfully', 'filename': filename}), 200

if __name__ == '__main__':
    app.run(debug=True)

