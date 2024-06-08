from flask import request, jsonify
import os
from werkzeug.utils import secure_filename
from src import web_api

# Define the upload folder
UPLOAD_FOLDER = os.path.dirname(__file__) + 'uploads'
web_api.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@web_api.route('/upload-image', methods=['POST'])
def upload_image():
    # Check if the post request has the file part
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400
    
    file = request.files['image']
    
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Secure the filename and save it to the upload folder
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(web_api.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({"path": filepath}), 200