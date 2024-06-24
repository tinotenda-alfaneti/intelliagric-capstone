import logging
import schedule
import time
import requests
from threading import Thread
from network_utils import is_connected_to_internet
from app import WEATHER_API_KEY

logging.basicConfig(level=logging.DEBUG)

def check_weather():
    if not is_connected_to_internet():
        logging.info("Not connected to WiFi with internet access. Skipping weather check.")
        return False
    
    api_key = WEATHER_API_KEY
    city = "Kumasi"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data["weather"][0]["main"] == "Clear":
            logging.info("Weather is clear")
            return True
        logging.info(f'The weather is {data["weather"][0]["main"]}')
        return False
    except requests.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return False

def schedule_flight():
    logging.info("Flight scheduled")
    if check_weather():
        logging.info("Performing flight")
        from drone_control import perform_flight
        perform_flight()

schedule.every().day.at("12:00").do(schedule_flight)

def start_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)
