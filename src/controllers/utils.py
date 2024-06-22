from flask import request, jsonify, make_response
import os
from werkzeug.utils import secure_filename
from src import web_api, ORIGIN_URL, logging, api
from flask_restx import Resource, fields

UPLOAD_FOLDER = os.path.dirname(__file__) + '/uploads'
web_api.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ns_upload = api.namespace('upload', description='Image upload operations')

# Define the model for Swagger documentation
upload_response_model = ns_upload.model('Upload', {
    'image': fields.String(required=True, description='Path to the crop image')
})
upload_model = ns_upload.model('UploadImage', {
    'image': fields.Raw(required=True, description='Image file to upload')
})

# Create the resource class for the image upload endpoint
@ns_upload.route('/image')
class UploadImageResource(Resource):
    @ns_upload.expect(upload_model)
    @ns_upload.response(200, 'Success', model=upload_response_model)
    @ns_upload.response(400, 'Bad Request')
    def post(self):
        """Uploads an image and returns the file path."""
        if 'image' not in request.files:
            return jsonify({"error": "No image part in the request"}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(web_api.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return jsonify({"path": filepath}), 200
            
api.add_namespace(ns_upload, path='/upload')
    
# --------------------- handle all preflight requests

@web_api.route('/get_soil_data', methods=['OPTIONS'])
@web_api.route('/soil_analysis', methods=['OPTIONS'])
@web_api.route('/chat', methods=['OPTIONS'])
@web_api.route('/query_ecommerce/', methods=['OPTIONS'])
@web_api.route('/predict_market', methods=['OPTIONS'])
@web_api.route('/predict_disease', methods=['OPTIONS'])
@web_api.route('/upload/image', methods=['OPTIONS'])
@web_api.route('/farm/overview', methods=['OPTIONS'])
@web_api.route('/farm/register', methods=['OPTIONS'])
@web_api.route('/auth/login', methods=['OPTIONS'])
@web_api.route('/auth/logout', methods=['OPTIONS'])

def handle_options():
    logging.info("Started the preflight handling")
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", ORIGIN_URL)
    response.headers.add("Access-Control-Allow-Headers", "Authorization, Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.status_code = 200
    return response