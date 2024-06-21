from src import ORIGIN_URL, web_api, api, Resource, fields, logging
from flask import request, jsonify, session, make_response
import os
from src.models.chat import Chat
from src.models.chat import CHAT_PROMPT
from src.models.firebase import Firebase
from src.models.predictions import Predict
from src.auth.auth import login_required

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define the namespaces
ns_chat = api.namespace('chat', description='Chat operations')

HISTORY_LIMIT = 10

# Define the models for Swagger documentation
message_model = api.model('Message', {
    'message': fields.String(required=True, description='User input message')
})

single_message_model = api.model('SingleMessage', {
    'role': fields.String(required=True, description='Whether the message is from User or Assistant'),
    'content': fields.String(required=True, description='The message'),
    'timestamp': fields.DateTime(required=True, description='The date and time the message was sent')
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

@ns_chat.route('/save')
class ChatResource(Resource):
    @login_required
    @ns_chat.expect(single_message_model)
    @ns_chat.response(200, 'Success')
    def post(self):
        """Saves chat messages from the user and assistant."""
        user_input = request.json

        add_response = Firebase.save_chat(user_input)

        if "error" in add_response:
            return jsonify({"error" : "Message not saved"})

        return jsonify({"success" : "Message saved successfully"})  
    
api.add_namespace(ns_chat, path='/chat')
api.add_namespace(ns_chat, path='/chat/save')