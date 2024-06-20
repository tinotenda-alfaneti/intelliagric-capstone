from flask import request, jsonify, make_response
import os
from werkzeug.utils import secure_filename
from src import web_api, ORIGIN_URL, logging

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
    
# --------------------- handle all preflight requests

@web_api.route('/get-soil-data', methods=['OPTIONS'])
@web_api.route('/soil-analysis', methods=['OPTIONS'])
@web_api.route('/chat', methods=['OPTIONS'])
@web_api.route('/query-ecommerce', methods=['OPTIONS'])
@web_api.route('/predict-market', methods=['OPTIONS'])
@web_api.route('/predict-disease', methods=['OPTIONS'])

def handle_options():
    logging.info("Started the preflight handling")
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", ORIGIN_URL)
    response.headers.add("Access-Control-Allow-Headers", "Authorization, Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.status_code = 200
    return response