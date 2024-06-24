from flask import jsonify, request
import threading
from datetime import datetime
import atexit
import requests
from src.models.chat import Chat
from src.auth.auth import login_required
from src import logging, web_api, db, api, Resource, fields, scheduler
from src.models.firebase import Firebase

user_token = web_api.config["AUTH_TOKEN"]

ns_soil_data = api.namespace('get_soil_data', description='Soil data from IoT device readings')
ns_soil_analysis = api.namespace('soil_analysis', description='Soil Analysis from IoT device data')
ns_daily_averages = api.namespace('daily_averages', description='Daily averages for the current user')

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


# Store the accumulated data
# TODO: In-Memory Data Store with Persistent Backup or Caching with Disk-based Cache
'''
Use an in-memory data structure like a dictionary and periodically back it up to a 
file (e.g., JSON) to persist data across restarts.
Caching with Disk-based Cache:
Use a caching library like diskcache, which stores data in 
memory with an option to spill over to disk, providing both speed and persistence.

'''
accumulated_data = {
    'mois': [],
    'ph': [],
    'npk': [],
    'temp': []
}

data_lock = threading.Lock()

# Function to transfer data
def transfer_data(event):
    with data_lock:
        try:
            logging.debug(f"Event received: {event.path} - {event.data}")
            if event.path == '/mois':
                if event.data is not None:
                    accumulated_data['mois'].append(event.data)
                    logging.debug(f"Accumulated moisture data: {accumulated_data['mois']}")
            elif event.path == '/ph':
                if event.data is not None:
                    accumulated_data['ph'].append(event.data)
                    logging.debug(f"Accumulated pH data: {accumulated_data['ph']}")
            elif event.path == '/npk':
                if event.data is not None:
                    accumulated_data['npk'].append(event.data)
                    logging.debug(f"Accumulated NPK data: {accumulated_data['npk']}")
            elif event.path == '/temp':
                if event.data is not None:
                    accumulated_data['temp'].append(event.data)
                    logging.debug(f"Accumulated temperature data: {accumulated_data['temp']}")
        except Exception as e:
            logging.error(f"Error in transfer_data: {e}")

# Function to watch the Realtime Database
def watch_realtime_db():
    try:
        user_token = web_api.config["AUTH_TOKEN"]
        initial_data = db.reference(f'iot/{user_token}').get()
        logging.debug(f"Initial data: {initial_data}")
        if initial_data:
            if 'mois' in initial_data and initial_data['mois'] is not None:
                accumulated_data['mois'].append(initial_data['mois'])
                logging.debug(f"Initial accumulated moisture data: {accumulated_data['mois']}")
            if 'npk' in initial_data and initial_data['npk'] is not None:
                accumulated_data['npk'].append(initial_data['npk'])
                logging.debug(f"Initial accumulated npk data: {accumulated_data['npk']}")
            if 'temp' in initial_data and initial_data['temp'] is not None:
                accumulated_data['temp'].append(initial_data['temp'])
                logging.debug(f"Initial accumulated temp data: {accumulated_data['temp']}")
            if 'ph' in initial_data and initial_data['ph'] is not None:
                accumulated_data['ph'].append(initial_data['ph'])
                logging.debug(f"Initial accumulated pH data: {accumulated_data['ph']}")
        db.reference(f'iot/{user_token}').listen(transfer_data)
        logging.info("Started listening to Realtime Database")
        
    except Exception as e:
        logging.error(f"Error in watch_realtime_db: {e}")

# Function to calculate daily average and save to Firestore
def save_daily_average():
    with data_lock:
        try:
            logging.debug("Calculating daily averages and saving to Firestore.")
            avg_data = {}
            if accumulated_data['mois']:
                avg_mois = sum(accumulated_data['mois']) / len(accumulated_data['mois'])
                avg_data['mois'] = avg_mois
                logging.info(f"Saved mois average: {avg_mois}")
            if accumulated_data['npk']:
                #TODO: Implement NPK calculation when actual value is found
                avg_data['npk'] = accumulated_data['npk']
                logging.info(f"Saved npk average: {accumulated_data['npk']}")
            if accumulated_data['temp']:
                avg_temp = sum(accumulated_data['temp']) / len(accumulated_data['temp'])
                avg_data['temp'] = avg_temp
                logging.info(f"Saved temp average: {avg_temp}")
            if accumulated_data['ph']:
                avg_ph = sum(accumulated_data['ph']) / len(accumulated_data['ph'])
                avg_data['ph'] = avg_ph
                logging.info(f"Saved pH average: {avg_ph}")
            if avg_data:
                avg_data['timestamp'] = datetime.now()
                Firebase.save_average_data(avg_data, user_token=web_api.config["AUTH_TOKEN"])
                logging.debug("Saved daily averages")
            # Clear the accumulated data for the next day
            accumulated_data['mois'].clear()
            accumulated_data['npk'].clear()
            accumulated_data['ph'].clear()
            accumulated_data['temp'].clear()
            logging.debug("Cleared accumulated data for the next day.")

        except Exception as e:
            logging.error(f"Error in save_daily_average: {e}")

if scheduler.running:
    # Ensure the scheduler shuts down when the app exits
    atexit.register(lambda: scheduler.shutdown())

# API endponpk to fetch the latest accumulated data
@ns_soil_data.route('/')
class SoilDataResource(Resource):
    @login_required
    @ns_soil_data.response(200, 'Success', [soil_data_model])
    @ns_soil_data.doc(security='Bearer Auth')
    def get(self):

        with data_lock:
            mois_data = accumulated_data['mois'][-1] if accumulated_data['mois'] else None
            npk_data = accumulated_data['npk'][-1] if accumulated_data['npk'] else None
            temp_data = accumulated_data['temp'][-1] if accumulated_data['temp'] else None
            ph_data = accumulated_data['ph'][-1] if accumulated_data['ph'] else None

            return jsonify({
                "mois": mois_data,
                "npk": npk_data,
                "temp": temp_data,
                "ph": ph_data
            })
    
@ns_soil_analysis.route('/')
class SoilAnalysisResource(Resource):
    @login_required
    @ns_soil_analysis.response(200, 'Success', [analysis_response_model])
    @ns_soil_data.doc(security='Bearer Auth')
    def get(self):

        user_token = web_api.config["AUTH_TOKEN"]
        get_data_response = requests.get(f'{request.url_root}/get_soil_data', headers={"Authorization": f"Bearer {user_token}"})

        if get_data_response.status_code != 200:
            return jsonify({"error": "Failed to retrieve data"}), 500
        
        data = get_data_response.json()
        analysis = Chat.soil_analysis(data)
        return jsonify({"analysis": analysis.strip()})

@ns_daily_averages.route('/')
class DailyAveragesResource(Resource):
    @login_required
    @ns_daily_averages.response(200, 'Success', averages_list_model)
    @ns_daily_averages.doc(security='Bearer Auth')
    def get(self):

        user_token = web_api.config["AUTH_TOKEN"]
        try:
            averages = Firebase.get_average_data(user_token)
            return jsonify({'averages': averages})
        except Exception as e:
            logging.error(f"Error fetching daily averages: {e}")
            return jsonify({"error": "Failed to retrieve daily averages"}), 500

# Start watching the database as soon as log in is successful
def start_transfer():

    try:
        transfer_thread = threading.Thread(target=watch_realtime_db)
        transfer_thread.daemon = True
        transfer_thread.start()
        logging.info("Transfer started")

    except Exception as e:
        logging.error(f"Error in start_transfer: {e}")

api.add_namespace(ns_daily_averages, path='/daily_averages')
api.add_namespace(ns_soil_analysis, path='/soil_analysis')
api.add_namespace(ns_soil_data, path='/get_soil_data')