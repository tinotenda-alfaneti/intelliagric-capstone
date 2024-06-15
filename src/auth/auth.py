
from src import auth, logging
from functools import wraps
from flask import request, jsonify

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

def verify_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        logging.info(f"The decoded token is: {decoded_token}")
        return decoded_token
    except Exception as e:
        logging.error(f"Token verification failed: {e}")
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
    