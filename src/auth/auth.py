
from src import logging
from firebase_admin import auth
from functools import wraps
from flask import request, jsonify

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

#TODO: Put back the token

def verify_id_token(uid):
    try:
        user = auth.get_user(uid)
        logging.info(f"Verification for {user} successful")
        return user
    except auth.AuthError as e:
        logging.error(f"Verification failed {e}")
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logging.debug("login_required decorator is called")
        auth_header = request.headers.get('Authorization')
        logging.debug(f"Authorization header: {auth_header}")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            response = jsonify({"error": "Authorization token is missing or invalid"})
            response.status_code = 401
            return response

        id_token = auth_header.split('Bearer ')[-1]
        decoded_token = verify_id_token(id_token)
        if decoded_token is None:
            response = jsonify({"error": "Invalid token"})
            response.status_code = 401
            return response

        return f(*args, **kwargs)
    return decorated_function
    