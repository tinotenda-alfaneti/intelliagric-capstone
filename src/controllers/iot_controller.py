import json
import logging
from flask import jsonify, request
import requests
from src.config.config import Config
from src.controllers.error_controller import handle_errors
from src.models.chat import Chat
from src.auth.auth import login_required
from src import web_api, api
from src.models.firebase import Firebase
from src.models.utils import API
from src.models.iot_service import data_lock, cache
from src.config.db_config import bucket
from flask_restx import fields, Resource

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

user_token = Config.AUTH_TOKEN

ns_soil_data = api.namespace('get_soil_data', description='Soil data from IoT device readings')
ns_soil_analysis = api.namespace('soil_analysis', description='Soil Analysis from IoT device data')
ns_daily_averages = api.namespace('daily_averages', description='Daily averages for the current user')
ns_drone_image_analysis = api.namespace('drone_image_analysis', description='Drone Image Analysis from captured images')

# Define the models for Swagger documentation
soil_data_model = api.model('SoilData', {
    'mois': fields.Float(required=True, description='Latest moisture data'),
    'npk': fields.String(required=True, description='Latest NPK data'),
    'temp': fields.Float(required=True, description='Latest temperature data'),
    'ph': fields.Float(required=True, description='Latest pH data'),
    'serialnum': fields.Float(required=True, description='Latest pH data')
}) 
analysis_response_model = api.model('AnalysisResponse', {
    'analysis': fields.String(description='Analysis of soil data')
})

average_data_model = api.model('AverageData', {
    'timestamp': fields.DateTime(description='Timestamp of the average data'),
    'mois': fields.Float(description='Average moisture data'),
    'npk': fields.String(description='Average NPK data'),
    'temp': fields.Float(description='Average temperature data'),
    'ph': fields.Float(description='Average pH data')
})

averages_list_model = api.model('AveragesList', {
    'averages': fields.List(fields.Nested(average_data_model), description='List of daily averages')
})

image_analysis_response_model = api.model('ImageAnalysisResponse', {
    'analysis': fields.String(description='Analysis of drone images')
})

# API endpoint to fetch the latest accumulated data
@ns_soil_data.route('/')
class SoilDataResource(Resource):
    @login_required
    @handle_errors
    @ns_soil_data.response(200, 'Success', [soil_data_model])
    @ns_soil_data.doc(security='Bearer Auth')
    def get(self):
        with data_lock:
            mois_data = cache.get('mois', [])
            npk_data = cache.get('npk', [])
            temp_data = cache.get('temp', [])
            ph_data = cache.get('ph', [])

            # Extract the most recent values
            mois_value = mois_data[-1]['value'] if mois_data else None
            npk_value = npk_data[-1]['value'] if npk_data else None
            temp_value = temp_data[-1]['value'] if temp_data else None
            ph_value = ph_data[-1]['value'] if ph_data else None

            return jsonify({
                "mois": mois_value,
                "npk": npk_value,
                "temp": temp_value,
                "ph": ph_value
            })
    
@ns_soil_analysis.route('/')
class SoilAnalysisResource(Resource):
    @login_required
    @handle_errors
    @ns_soil_analysis.response(200, 'Success', [analysis_response_model])
    @ns_soil_data.doc(security='Bearer Auth')
    def get(self):
        user_token = Config.AUTH_TOKEN
        get_data_response = requests.get(f'{request.url_root}/get_soil_data', headers={"Authorization": f"Bearer {user_token}"})

        if get_data_response.status_code != 200:
            return jsonify({"error": "Failed to retrieve data"}), 500
        
        data = get_data_response.json()
        analysis = Chat.soil_analysis(data)
        return jsonify({"analysis": analysis.strip()})

@ns_daily_averages.route('/')
class DailyAveragesResource(Resource):
    @login_required
    @handle_errors
    @ns_daily_averages.response(200, 'Success', averages_list_model)
    @ns_daily_averages.doc(security='Bearer Auth')
    def get(self):
        user_token = Config.AUTH_TOKEN
        try:
            averages = Firebase.get_average_data(user_token)
            return jsonify({'averages': averages})
        except Exception as e:
            logging.error(f"Error fetching daily averages: {e}")
            return jsonify({"error": "Failed to retrieve daily averages"}), 500
        
@ns_drone_image_analysis.route('/')
class DroneImageAnalysisResource(Resource):
    @login_required
    @handle_errors
    @ns_drone_image_analysis.response(200, 'Success', [image_analysis_response_model])
    @ns_drone_image_analysis.doc(security='Bearer Auth')
    def get(self):
        user_token = Config.AUTH_TOKEN

        try:
            blobs = bucket.list_blobs(prefix=f'drone_images/{user_token}/')

            image_urls = []
            for blob in blobs:
                image_url = blob.public_url
                image_urls.append(image_url)

            if not image_urls:
                return jsonify({"error": "No images found for analysis"}), 404

            user_input = "These are images from the drone as it was capturing images around the farm. Please provide an analysis and recommendation on whether I should watch out for any potential diseases. "
            identification = API.identify(image_urls, flag=0)
            best_suggestion = max(identification['result']['disease']['suggestions'], key=lambda x: x['probability'])['name']
            analysis_response =  {"disease": best_suggestion, "detailed_info": json.dumps(identification)}

            refined_response = Chat.refine_response(user_input, analysis_response)

            return jsonify({"analysis": refined_response})
        
        except Exception as e:
            logging.error(f"Error in DroneImageAnalysisResource: {e}")
            return jsonify({"error": "Failed to retrieve and analyze images"}), 500

api.add_namespace(ns_daily_averages, path='/daily_averages')
api.add_namespace(ns_soil_analysis, path='/soil_analysis')
api.add_namespace(ns_soil_data, path='/get_soil_data')
api.add_namespace(ns_drone_image_analysis, path='/drone_image_analysis')
