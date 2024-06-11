from src import web_api
from flask import request, jsonify, session
import os
from src.models.chat import Chat
from src.models.chat import CHAT_PROMPT
from src.models.predictions import Predict

HISTORY_LIMIT = 10

TEST_IMG = os.path.dirname(__file__) + "/uploads/example.jpg"
#TODO: Fix this so that data coming can have varying item name. The chat model should capture the crop also and return in as part of the response
TEST_DATA = {
    "area": "Ghana",
    "item": "Maize"
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

    return jsonify({'message': intent_response})

@web_api.route('/predict-disease', methods=['GET'])
def predict_disease():

    crop_img =  request.json.get('path')
    user_input = request.json.get('message')
    #TODO: Add another intent for diseases that are not for maize and then use the API from kindwise

    model_response = Predict.maize_disease_prediction(crop_img)
    print(model_response)
    refined_response = Chat.refine_response(user_input, model_response)
    session['conversation_history'].append({"role": "assistant", "content": refined_response})
    return jsonify({'intent': 'predict maize disease', 'message': refined_response})

@web_api.route('/predict-market', methods=['GET'])
def predict_market():
    
    user_data = {
        "area": request.json.get("area"),
        "item": request.json.get("item")
    }
    user_input = request.json.get("message")
    
    market_response = Predict.market_prediction(user_data)
    refined_response = Chat.refine_response(user_input, market_response)
    session['conversation_history'].append({"role": "assistant", "content": refined_response})
    return jsonify({'intent': 'predict agriculture market', 'message': refined_response})

