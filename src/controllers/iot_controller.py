from flask import jsonify, render_template, request
import threading
from datetime import datetime
import atexit
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from src.models.chat import Chat
from src import logging, web_api, database, db_ref, OPENAI_API_KEY, api, Resource, fields


ns_soil_data = api.namespace('get-soil-data', description='Soil data from IoT device readings')
ns_soil_analysis = api.namespace('soil-analysis', description='Soil Analysis from IoT device data')

# Define the models for Swagger documentation
soil_data_model = api.model('SoilData', {
    'mois': fields.Float(required=True, description='Latest moisture data'),
    'npk': fields.String(required=True, description='Latest NPK data'),
    'temp': fields.Float(required=True, description='Latest temperature data'),
    'ph': fields.Float(required=True, description='Latest pH data')
})

analysis_response_model = api.model('AnalysisResponse', {
    'analysis': fields.String(description='Analysis of soil data')
})

# Store the accumulated data
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
        
        initial_data = db_ref.get()
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
        db_ref.listen(transfer_data)
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
                database.collection('daily_averages').add(avg_data)
                logging.debug("Saved daily averages")
            # Clear the accumulated data for the next day
            accumulated_data['mois'].clear()
            accumulated_data['npk'].clear()
            accumulated_data['ph'].clear()
            accumulated_data['temp'].clear()
            logging.debug("Cleared accumulated data for the next day.")
        except Exception as e:
            logging.error(f"Error in save_daily_average: {e}")

# Schedule the save_daily_average function to run at midnight
scheduler = BackgroundScheduler()
scheduler.add_job(func=save_daily_average, trigger='cron', hour=0, minute=0)
# uncomment for testing
# scheduler.add_job(func=save_daily_average, trigger='interval', seconds=60)
scheduler.start()

# Ensure the scheduler shuts down when the app exits
atexit.register(lambda: scheduler.shutdown())

# API endponpk to fetch the latest accumulated data
@ns_soil_data.route('/')
class SoilDataResource(Resource):
    @ns_soil_data.response(200, 'Success', [soil_data_model])
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
    @ns_soil_analysis.response(200, 'Success', [analysis_response_model])
    def get(self):
        # Step 1: Call the /get-data endpoint to retrieve the latest accumulated data
        get_data_response = requests.get(f'{request.url_root}/get-soil-data')
        
        if get_data_response.status_code != 200:
            return jsonify({"error": "Failed to retrieve data"}), 500
        
        data = get_data_response.json()
        
        analysis = Chat.soil_analysis(data)
        
        return jsonify({"analysis": analysis.strip()})

# Serve the HTML file
@web_api.route('/test')
def test():
    return render_template('index.html.j2')

# Start watching the database as soon as the app starts
@web_api.before_first_request
def start_transfer():
    try:
        transfer_thread = threading.Thread(target=watch_realtime_db)
        transfer_thread.daemon = True
        transfer_thread.start()
        logging.info("Transfer started")
    except Exception as e:
        logging.error(f"Error in start_transfer: {e}")

# Add the namespace to the API
api.add_namespace(ns_soil_analysis, path='/soil-analysis')
api.add_namespace(ns_soil_data, path='/soil-data')
