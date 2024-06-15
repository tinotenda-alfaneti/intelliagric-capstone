import os
from datetime import timedelta

from flask import Flask, session
from flask_session import Session
from flask_cors import CORS
from flask_restx import Api, Resource, fields

import firebase_admin
from firebase_admin import credentials, storage, firestore, db, auth

import openai
from dotenv import load_dotenv
import logging
from newsapi import NewsApiClient

web_api = Flask("src")

# Session Configuration
web_api.config["SESSION_PERMANENT"] = False
web_api.config["SESSION_TYPE"] = "filesystem"
web_api.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=45)
Session(web_api)

ORIGIN_URL = "http://localhost:3000" #TODO: Replace with the deployed version

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
API_KEY = os.getenv('API_KEY')
PROJECT_ID = os.getenv('PROJECT_ID')
PRIVATE_KEY_ID = os.getenv('PRIVATE_KEY_ID')
CLIENT_CERT = os.getenv('CLIENT_CERT')
AUTH_PROVIDER_CERT = os.getenv('AUTH_PROVIDER_CERT')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HF_TOKEN = os.getenv('HF_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
GNEWS_API_KEY = os.getenv('GNEWS_API_KEY')
KINDWISE_API_KEY = os.getenv('KINDWISE_API_KEY')

# Configure Firebase
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": PROJECT_ID,
  "private_key_id": PRIVATE_KEY_ID,
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCpfik1HPptZzcG\nkrfQXKAGG8Moglb4WZEse3PWJC8O//l9IHSZkRkRVKeW1RWYDN4OwAfwVjTyD8Zl\ntNgioRNhSXnp8grswhucoi+BCPzJ+h2H/RvgHcFJvScsFxxpsoPCZT9tGQZuPXGL\n7KmQSYzHnOXq25kMdFRgoZj3uur7yYb8sf6vqmAxV9E53zQZUNiFctqHP4Bs528g\nSJTRCJHqLMUXjZCi7e1l+DzWAa4niluaqT1er2ppoaD6wiOVer9FlIwp/DJKTpNf\nZdH7WZWKYISmYcg975SxLGheXXjeWuHT+pHz/qgA429EmIavA+d6PZJ8sK1vbu7Y\na+gsMtDLAgMBAAECggEACzt8UUlGLVmRk3gbV2MetcOW54iFE/iiPs+VnyOPEiWT\nlp+/1ReBEPLKbRwE+NUizYPGDZQ2S7O7mFeSRUU7IA+QVUPVm9gcoADoOLBsSZmv\nkFNioAkeG0a+TFU3Fv1zbulqeSPslwIFFC/5vWv/uOYkdIUwu4W6u8apzle5pThG\nLdF0F/sakd2hfl/wxR9ktrwlShQiYlEFwlivUFJRo7du6xC6/ZVOFAB2rwsld14v\nZuiQBdRbTIYpfkk8Y5isEFEI9qVf6+xmjATIFSB4Z812RLOtQg9ogbN+T9XeKax9\nNNaepKu1TWgU9n/tqfy15rXMRDp5wNRIvlEhQzKORQKBgQDoqZM9nO2/NQv+PxmG\n90cDnem5L7qWmpHucNQhnW/GQvLZkhnT6XpmtZS2dYi7cUcCfXj/19Y0ml2tJVNh\nH7ykSZaSNBK/4vMmV0vjcwkXxDfVtAHsPSr1F/ZIrZHwMp6nxmfRG/ajDRl4MfhE\nVzZ/6VU5xCnUnw27817lNVS8VwKBgQC6fnwThNbTe2Kuxz/5jxLZiyaJWoAVDKxw\ne9VzgXZ5Jn11/59pKe/MXIUfFBoZH1cJ8qS0zfr3nKo/UEG3ehdJbCKudp+0eymm\nb+4SdDOtD1M06jlQG2kPpJtqtzgWb8BrNkOdBM6y3f8hNlobbQJ4RXLYQKvTNMwH\nbZIXOzaGrQKBgBQdZQ90m9FmIq1Og0R56HfVlTlfeQBASNGWi6CEXf+EFj7dNMJv\ncxeiJ0NHEhUyi/MZKfbkkC5oEiVADt9cwRBrFEt7mQth8aek8Hivn1+gpTsinu/v\nseESu0Y5S1664aCbtKoNgttB7KvJli9CYwHYCHhAD2XEgol3VwL2A2dtAoGAQfQD\nWz/KXYYwMxFiDZbMmsS8Py0TSN5viWQx66RoSpYTHozlSmK7XHGH3qLUS/gqZuk5\n2HtT+webqcJvSzzRSXUFmt92wXQhGaxR7JLNx7E4wujmle7rq82R7R6Ypk6lJQVO\nyhPuKZGa7Zr0KOjXS8N7xwCwA4STdzkHxlF5ig0CgYEAgoIzYv6f0JD/K3gisn2T\n5nsmcLPCWvKW3Hug6JtF/RVzF9bx0msOdRzVHspH5h8kTzIrpZ4dynbf/bs1lT3n\n3fCmEb95xd0X2rja6VcRZJyIyqSnV5KWSp3I+UpgsRmAeK/RxC0l4Zj9zDgtCCVi\nM99f7t1TiYV0BxhFRxYFJvw=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-bb0mb@intelliagric-c1df6.iam.gserviceaccount.com",
  "client_id": "116790317060513119402",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": AUTH_PROVIDER_CERT,
  "client_x509_cert_url": CLIENT_CERT,
  "universe_domain": "googleapis.com"
  
})
firebase_admin.initialize_app(credential=cred, options={'storageBucket': 'intelliagric-c1df6.appspot.com', 'databaseURL': 'https://intelliagric-c1df6-default-rtdb.firebaseio.com'})
bucket = storage.bucket()
database = firestore.client()
client = openai.OpenAI(api_key=OPENAI_API_KEY)
newsapi = NewsApiClient(api_key=NEWS_API_KEY)
from src.controllers import *
