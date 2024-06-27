import os
from datetime import timedelta

from flask import Flask, request
from flask_session import Session
from flask_cors import CORS
from flask_restx import Api

from dotenv import load_dotenv
from newsapi import NewsApiClient
from src.config.db_config import cred

from twilio.rest import Client

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import signal
import atexit

from src.models.disease_alerts_service import DiseaseAlerts
from src.models.iot_service import check_transfer, clean_old_data, save_daily_average


web_api = Flask("src")

# Session Configuration
web_api.config["SESSION_PERMANENT"] = False
web_api.config["SESSION_TYPE"] = "filesystem"
web_api.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=45)


Session(web_api)

ORIGIN_URL = "http://localhost:3000" #TODO: Replace with the deployed version
# deployed version = https://intelli-agric-react-m81e69i71.vercel.app/

# secre key
web_api.secret_key = os.urandom(24)

CORS(web_api, supports_credentials=True, resources={r"/*": {"origins": ORIGIN_URL}})

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

# initialize API documentation
api = Api(web_api, version='1.0', 
          title='IntelliAgric API', 
          description='An Intelligent Farming Assistant API',
          authorizations=authorizations,
          security='Bearer Auth')

# load private keys from dotenv
load_dotenv('.env')
HF_TOKEN = os.getenv('HF_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
GNEWS_API_KEY = os.getenv('GNEWS_API_KEY')
KINDWISE_API_KEY = os.getenv('KINDWISE_API_KEY')
TWILIO_SID=os.getenv('TWILIO_SID')
TWILIO_AUTH=os.getenv('TWILIO_AUTH')
TWILIO_NUM=os.getenv('TWILIO_NUM')
DB_USER=os.getenv('DB_USER')
DB_HOST=os.getenv('DB_HOST')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_NAME=os.getenv('DB_NAME')

newsapi = NewsApiClient(api_key=NEWS_API_KEY)
twilio_client = Client(TWILIO_SID, TWILIO_AUTH)
from src.controllers import *

# Configure the APScheduler
executors = {
    'default': ThreadPoolExecutor(10),
    'processpool': ProcessPoolExecutor(5)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 5
}

scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
scheduler.start()

#register jobs
scheduler.add_job(func=DiseaseAlerts.check_disease_predictions, trigger='cron', hour=0, minute=0)
scheduler.add_job(func=clean_old_data, trigger='interval', hours=1)
scheduler.add_job(func=check_transfer, trigger='interval', minutes=1)
scheduler.add_job(func=save_daily_average, trigger='interval', seconds=60)

# shutdown function
#TODO: Add flask stop also in the function

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

# def shutdown_scheduler():
#     print("Shutting down scheduler...")
#     scheduler.shutdown(wait=False)
#     shutdown_server()

# # Register shutdown signals
# signal.signal(signal.SIGINT, lambda signum, frame: shutdown_scheduler())
# signal.signal(signal.SIGTERM, lambda signum, frame: shutdown_scheduler())



# Register atexit handler
if scheduler.running:
  atexit.register(lambda: scheduler.shutdown())