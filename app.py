from flask import Flask, jsonify
from weather_check import schedule_flight
from firebase_upload import get_latest_image_urls
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv('.env')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
BUCKET = os.getenv('BUCKET')
WIFI_SSID = os.getenv('WIFI_SSID')
WIFI_PASSWORD = os.getenv('WIFI_PASSWORD')
TELLO_SSID = os.getenv('TELLO_SSID')

@app.route('/analyze', methods=['GET'])
def analyze_images():
    urls = get_latest_image_urls()
    return jsonify({'image_urls': urls})

if __name__ == "__main__":
    schedule_flight()
    app.run(host='0.0.0.0', port=5000)
