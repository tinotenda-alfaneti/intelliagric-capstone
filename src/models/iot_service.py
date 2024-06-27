import threading
import time
from datetime import datetime
import atexit
import diskcache as dc
from src import logging, web_api, db, scheduler
from src.models.firebase import Firebase

user_token = web_api.config["AUTH_TOKEN"]

cache = dc.Cache('cache_directory')

data_lock = threading.Lock()

# Function to transfer data
def transfer_data(event):
    with data_lock:
        try:
            logging.debug(f"Event received: {event.path} - {event.data}")
            if event.data is not None:
                sensor_type = event.path.strip('/')
                if sensor_type in ['mois', 'ph', 'npk', 'temp']:
                    add_data(sensor_type, event.data)
                    logging.debug(f"Accumulated {sensor_type} data: {cache.get(sensor_type)}")
        except Exception as e:
            logging.error(f"Error in transfer_data: {e}")

def add_data(sensor_type, value):
    timestamp = time.time()
    if sensor_type in cache:
        cache[sensor_type].append({'timestamp': timestamp, 'value': value})
    else:
        cache[sensor_type] = [{'timestamp': timestamp, 'value': value}]
    clean_old_data()

def get_data(sensor_type):
    if sensor_type in cache:
        return [entry['value'] for entry in cache[sensor_type]]
    return []

# Function to clean old data from the cache
def clean_old_data():
    threshold = time.time() - 24 * 3600
    for sensor_type in cache:
        cache[sensor_type] = [entry for entry in cache[sensor_type] if entry['timestamp'] >= threshold]

# Schedule periodic cleanup every hour is default
def schedule_cleanup(interval=3600):
    clean_old_data()
    threading.Timer(interval, schedule_cleanup, [interval]).start()

schedule_cleanup()

def watch_realtime_db():
    try:
        user_token = web_api.config["AUTH_TOKEN"]
        initial_data = db.reference(f'iot/{user_token}').get()
        logging.debug(f"Initial data: {initial_data}")
        if initial_data:
            for sensor_type in ['mois', 'npk', 'temp', 'ph']:
                if sensor_type in initial_data and initial_data[sensor_type] is not None:
                    add_data(sensor_type, initial_data[sensor_type])
                    logging.debug(f"Initial accumulated {sensor_type} data: {cache.get(sensor_type)}")
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
            for sensor_type in ['mois', 'npk', 'temp', 'ph']:
                sensor_values = get_data(sensor_type)
                if sensor_values:
                    avg_data[sensor_type] = sum(sensor_values) / len(sensor_values)
                    logging.info(f"Saved {sensor_type} average: {avg_data[sensor_type]}")
            if avg_data:
                avg_data['timestamp'] = datetime.now()
                Firebase.save_average_data(avg_data, user_token=web_api.config["AUTH_TOKEN"])
                logging.debug("Saved daily averages")

            # Clear the accumulated data for the next day
            for sensor_type in ['mois', 'npk', 'temp', 'ph']:
                cache[sensor_type] = []
            logging.debug("Cleared accumulated data for the next day.")

        except Exception as e:
            logging.error(f"Error in save_daily_average: {e}")

if scheduler.running:
    # Ensure the scheduler shuts down when the app exits
    atexit.register(lambda: scheduler.shutdown())

# Start watching the database as soon as log in is successful
def start_transfer(state):
    try:
        # Only start the transfer if it hasn't been started already
        if not state.transfer_started:
            transfer_thread = threading.Thread(target=watch_realtime_db)
            transfer_thread.daemon = True
            transfer_thread.start()
            logging.info("Transfer started")
            state.transfer_started = True
        else:
            logging.info("Transfer already running")
    except Exception as e:
        logging.error(f"Error in start_transfer: {e}")

# Close the cache on exit
atexit.register(lambda: cache.close())
