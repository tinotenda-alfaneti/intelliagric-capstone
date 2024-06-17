from src import ORIGIN_URL, web_api, api, Resource, fields, logging
from flask import request, jsonify, session, make_response
import os
from src.models.chat import Chat
from src.models.chat import CHAT_PROMPT
from src.models.predictions import Predict

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define the namespaces
ns_chat = api.namespace('chat', description='Chat operations')

HISTORY_LIMIT = 10

# Define the models for Swagger documentation
message_model = api.model('Message', {
    'message': fields.String(required=True, description='User input message')
})

TEST_IMG = os.path.dirname(__file__) + "/uploads/example.jpg"
TEST_DATA = {
    "area": "Ghana",
    "item": "Maize"
}


@ns_chat.route('/')
class ChatResource(Resource):
    @ns_chat.expect(message_model)
    @ns_chat.response(200, 'Success')
    def post(self):
        """Handles chat messages from the user."""
        user_input = request.json.get('message')
        
        if 'conversation_history' not in session:
            session['conversation_history'] = CHAT_PROMPT
        
        session['conversation_history'].append({"role": "user", "content": user_input})
        
        if len(session['conversation_history']) > HISTORY_LIMIT:
            session['conversation_history'] = session['conversation_history'][-HISTORY_LIMIT:]
        
        intent_response = Chat.get_intent_and_response(session['conversation_history'])

        #Intent response structure: {"intent": "intent_name", "key1": "value1", "key2": "value2", ...}

        session['conversation_history'].append({"role": "assistant", "content": intent_response})

        return jsonify({"response": intent_response, "chat_history": session['conversation_history']})
    

# handle preflight requests for chat
@web_api.route('/chat', methods=['OPTIONS'])
def chat_options():
    logging.info("Started the preflight handling")
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", ORIGIN_URL)
    response.headers.add("Access-Control-Allow-Headers", "Authorization, Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.status_code = 200
    return response
    
api.add_namespace(ns_chat, path='/chat')