from src import web_api
from flask import request, jsonify, session
import requests
import os
from src.models.chat import Chat
from src.models.chat import CHAT_PROMPT
from src.models.predictions import MARKET_MODEL_ENDPOINT, DISEASE_MODEL_ENDPOINT, Predict

HISTORY_LIMIT = 10
TEST_IMG = os.path.dirname(__file__) + "/uploads/example.jpg"
TEST_DATA = {
    "Area": "Ghana",
    "Item": "Maize",
    "average_rain_fall_mm_per_year": 1200,
    "avg_temp": 28.4
  }


'''
Example of input data:
#generate_answer(input_data)
{
    "message":"How can I farm maize?"
}
'''
@web_api.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    
    # Initialize conversation history if not present
    if 'conversation_history' not in session:
        session['conversation_history'] = CHAT_PROMPT
    
    # Append user's message to the conversation history
    session['conversation_history'].append({"role": "user", "content": user_input})
    
    # Limit the conversation history to the last 10 exchanges
    if len(session['conversation_history']) > HISTORY_LIMIT:
        session['conversation_history'] = session['conversation_history'][-HISTORY_LIMIT:]
    
    # Get the intent and initial response from the GPT model
    intent_response = Chat.get_intent_and_response(session['conversation_history'])

    #TODO: Add another intent for diseases that are not for maize and then use the API from kindwise

    if 'predict maize disease' in intent_response.lower():
        #TODO: Add functionality to take the image from the user and then use the path here
        model_response = Predict.maize_disease_prediction(TEST_IMG)
        print(model_response)
        refined_response = Chat.refine_response(user_input, model_response)
        session['conversation_history'].append({"role": "assistant", "content": refined_response})
        return jsonify({'intent': 'predict maize disease', 'message': refined_response})
    
    elif 'predict agriculture market' in intent_response.lower():
        market_response = Predict.market_prediction(TEST_DATA)
        refined_response = Chat.refine_response(user_input, market_response)
        session['conversation_history'].append({"role": "assistant", "content": refined_response})
        return jsonify({'intent': 'predict agriculture market', 'message': refined_response})
    else:
        # If intent is general, return the response directly
        session['conversation_history'].append({"role": "assistant", "content": intent_response})
        return jsonify({'intent': 'general', 'message': intent_response})

