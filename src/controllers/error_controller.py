from functools import wraps
from flask import jsonify
import logging
from src import session
from flask import jsonify

from src.models.chat import CHAT_PROMPT

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as error:
            
            if 'conversation_history' not in session:
                session['conversation_history'] = CHAT_PROMPT

            logging.exception('Server Error: %s', (error))
            
            response = "Sorry, I am having technical issues please try again in a moment",
            
            session['conversation_history'].append({"role": "assistant", "content": response})
            final_response = jsonify({"response": response, "chat_history": session['conversation_history']})

            final_response.status_code = 500
            return final_response
        
    return decorated_function
