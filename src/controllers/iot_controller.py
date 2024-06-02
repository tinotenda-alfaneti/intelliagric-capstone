from flask import jsonify, render_template
import threading
from datetime import datetime
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

from src import logging, web_api, database, db_ref

# Store the accumulated data
accumulated_data = {
    'float': [],
    'int': []
}

data_lock = threading.Lock()

# Function to transfer data
def transfer_data(event):
    with data_lock:
        try:
            logging.debug(f"Event received: {event.path} - {event.data}")
            if event.path == '/float':
                if event.data is not None:
                    accumulated_data['float'].append(event.data)
                    logging.debug(f"Accumulated float data: {accumulated_data['float']}")
            elif event.path == '/int':
                if event.data is not None:
                    accumulated_data['int'].append(event.data)
                    logging.debug(f"Accumulated int data: {accumulated_data['int']}")
        except Exception as e:
            logging.error(f"Error in transfer_data: {e}")

# Function to watch the Realtime Database
def watch_realtime_db():
    try:
        
        initial_data = db_ref.get()
        logging.debug(f"Initial data: {initial_data}")
        if initial_data:
            if 'float' in initial_data and initial_data['float'] is not None:
                accumulated_data['float'].append(initial_data['float'])
                logging.debug(f"Initial accumulated float data: {accumulated_data['float']}")
            if 'int' in initial_data and initial_data['int'] is not None:
                accumulated_data['int'].append(initial_data['int'])
                logging.debug(f"Initial accumulated int data: {accumulated_data['int']}")
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
            if accumulated_data['float']:
                avg_float = sum(accumulated_data['float']) / len(accumulated_data['float'])
                avg_data['float'] = avg_float
                logging.info(f"Saved float average: {avg_float}")
            if accumulated_data['int']:
                avg_int = sum(accumulated_data['int']) / len(accumulated_data['int'])
                avg_data['int'] = avg_int
                logging.info(f"Saved int average: {avg_int}")
            if avg_data:
                avg_data['timestamp'] = datetime.now()
                database.collection('daily_averages').add(avg_data)
                logging.debug("Saved daily averages")
            # Clear the accumulated data for the next day
            accumulated_data['float'].clear()
            accumulated_data['int'].clear()
            logging.debug("Cleared accumulated data for the next day.")
        except Exception as e:
            logging.error(f"Error in save_daily_average: {e}")

# Schedule the save_daily_average function to run at midnight
scheduler = BackgroundScheduler()
# scheduler.add_job(func=save_daily_average, trigger='cron', hour=0, minute=0)
# uncomment for testing
scheduler.add_job(func=save_daily_average, trigger='interval', seconds=60)
scheduler.start()

# Ensure the scheduler shuts down when the app exits
atexit.register(lambda: scheduler.shutdown())

# API endpoint to fetch the latest accumulated data
@web_api.route('/get-data', methods=['GET'])
def get_data():
    with data_lock:
        float_data = accumulated_data['float'][-1] if accumulated_data['float'] else None
        int_data = accumulated_data['int'][-1] if accumulated_data['int'] else None
        return jsonify({
            "float": float_data,
            "int": int_data
        })

# Serve the HTML file
@web_api.route('/test')
def test():
    return render_template('index.html')

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
