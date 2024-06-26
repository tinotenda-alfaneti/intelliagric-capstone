from src import ORIGIN_URL, web_api, api, Resource, fields, logging
from flask import request, jsonify, session, make_response
import os, json
from src.controllers.error_controller import handle_errors
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

saved_message_model = ns_chat.model('SavedMessage', {
    'user_id': fields.String(required=True, description='ID of the user'),
    'message': fields.String(required=True, description='The chat message'),
    'timestamp': fields.String(required=True, description='Timestamp of the message')
})

messages_response_model = ns_chat.model('SavedMessagesResponse', {
    'success': fields.String(required=True, description='Success message'),
    'messages': fields.List(fields.Nested(message_model), description='List of chat messages')
})

error_response_model = ns_chat.model('ErrorResponse', {
    'error': fields.String(required=True, description='Error message')
})

TEST_IMG = os.path.dirname(__file__) + "/uploads/example.jpg"
TEST_DATA = {
    "area": "Ghana",
    "item": "Maize"
}


@ns_chat.route('/')
class ChatResource(Resource):
    @handle_errors
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
    @handle_errors
    @login_required
    @ns_chat.expect(single_message_model)
    @ns_chat.response(200, 'Success')
    @ns_chat.response(400, 'Bad Request')
    @ns_chat.response(500, 'Internal Server Error')
    def post(self):
        """Saves chat messages from the user and assistant."""
        try:
            user_input = request.json
            if not user_input:
                return jsonify({"error": "Invalid input: No data provided"})

            add_response = Firebase.save_chat(user_input)
            response_data = json.loads(add_response)

            if "error" in response_data:
                return jsonify({"error": response_data["error"]})

            return jsonify({"success": "Message saved successfully"})
        
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format"})
        
        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"})

@ns_chat.route('/saved_chats')
class RetrieveChatResource(Resource):
    @login_required
    @handle_errors
    @ns_chat.response(200, 'Success', model=messages_response_model)
    @ns_chat.response(400, 'Bad Request', model=error_response_model)
    @ns_chat.response(500, 'Internal Server Error', model=error_response_model)
    def get(self):
        """Retrieves chat history saved by the user."""
        try:
            retrieve_response = Firebase.retrieve_saved_chats()
            response_data = json.loads(retrieve_response)
            
            if "error" in response_data:
                return jsonify({"error": response_data["error"]})

            return jsonify({"success": "Messages retrieved successfully", "messages": response_data["messages"]})

        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format"})

        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"})
  
    
api.add_namespace(ns_chat, path='/chat')
api.add_namespace(ns_chat, path='/chat/save')
api.add_namespace(ns_chat, path='/chat/saved_chats')