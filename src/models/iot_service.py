import logging
import threading
import time
from datetime import datetime
import atexit
import diskcache as dc
from src.config.config import Config
from firebase_admin import db
from src.models.firebase import Firebase

cache = dc.Cache('cache_directory')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

user_token = Config.AUTH_TOKEN

data_lock = threading.Lock()

# Function to transfer data
def transfer_data(event):
    try:
        logging.debug(f"Event received: {event.path} - {event.data}")
        if event.data is not None:
            sensor_type = event.path.strip('/')
            if sensor_type in ['mois', 'ph', 'npk', 'temp']:
                add_data(sensor_type, event.data)
                logging.debug(f"Accumulated {sensor_type} data: {get_data(sensor_type)}")
    except Exception as e:
        logging.error(f"Error in transfer_data: {e}")

def add_data(sensor_type, value):
    timestamp = time.time()
    logging.debug(f"Adding data: sensor_type={sensor_type}, value={value}, timestamp={timestamp}")
    with data_lock:
        data = cache.get(sensor_type, [])
        data.append({'timestamp': timestamp, 'value': value})
        cache[sensor_type] = data
        logging.debug(f"Current {sensor_type} cache: {cache.get(sensor_type, 'Not Found')}")


def get_data(sensor_type):
    if sensor_type in cache:
        return [entry['value'] for entry in cache[sensor_type]]
    return []

# Function to clean old data from the cache
def clean_old_data():
    threshold = time.time() - 24 * 3600
    logging.debug(f"Cleaning data older than: {threshold}")
    with data_lock:
        for sensor_type in list(cache.keys()):  # Convert to list to allow modification during iteration
            old_data = cache[sensor_type]
            cache[sensor_type] = [entry for entry in cache[sensor_type] if entry['timestamp'] >= threshold]
            logging.debug(f"Cleaned {sensor_type} cache. Before: {old_data}, After: {cache[sensor_type]}")


def watch_realtime_db():
    try:
        if Config.AUTH_TOKEN != 'none':
            user_token = Config.AUTH_TOKEN
            initial_data = db.reference(f'iot/{user_token}').get()
            logging.debug(f"Initial data: {initial_data}")
            if initial_data:
                for sensor_type in ['mois', 'npk', 'temp', 'ph']:
                    if sensor_type in initial_data and initial_data[sensor_type] is not None:
                        add_data(sensor_type, initial_data[sensor_type])
                        logging.debug(f"Initial accumulated {sensor_type} data: {cache.get(sensor_type)}")
            db.reference(f'iot/{user_token}').listen(transfer_data)
            logging.info("Started listening to Realtime Database")
        else:
            logging.info("AUTH_TOKEN is None, skipping save_daily_average.")
    except Exception as e:
        logging.error(f"Error in watch_realtime_db: {e}")

# Function to calculate daily average and save to Firestore
def save_daily_average():
    try:
        if Config.AUTH_TOKEN != 'none':
            logging.debug("Calculating daily averages and saving to Firestore.")
            avg_data = {}
            for sensor_type in ['mois', 'temp', 'ph']:
                sensor_values = get_data(sensor_type)
                if sensor_values:
                    avg_data[sensor_type] = sum(sensor_values) / len(sensor_values)
                    logging.info(f"Saved {sensor_type} average: {avg_data[sensor_type]}")
            if avg_data:
                avg_data['timestamp'] = datetime.now()
                Firebase.save_average_data(avg_data, user_token=Config.AUTH_TOKEN)
                logging.debug("Saved daily averages")

            # Clear the accumulated data for the next day
            for sensor_type in ['mois', 'npk', 'temp', 'ph']:
                with data_lock:
                    cache[sensor_type] = []
            logging.debug("Cleared accumulated data for the next day.")
        else:
            logging.info("AUTH_TOKEN is None, skipping save_daily_average.")
    except Exception as e:
        logging.error(f"Error in save_daily_average: {e}")

# Start watching the database as soon as log in is successful
def start_transfer():
    try:
        transfer_thread = threading.Thread(target=watch_realtime_db)
        transfer_thread.daemon = True
        transfer_thread.start()
        logging.info("Transfer started")
    except Exception as e:
        logging.error(f"Error in start_transfer: {e}")

def stop_transfer():
    Config.AUTH_TOKEN = 'none'
    logging.info("Transfer stopped")

def check_transfer():
    if Config.AUTH_TOKEN != 'none':
        start_transfer()
    else:
        stop_transfer()

# Close the cache on exit
atexit.register(lambda: cache.close())
