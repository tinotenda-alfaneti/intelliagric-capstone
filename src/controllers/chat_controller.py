from src import web_api, api, Resource, fields
from flask import request, jsonify, session
import os
from src.models.chat import Chat
from src.models.chat import CHAT_PROMPT
from src.models.predictions import Predict

# Define the namespaces
ns_chat = api.namespace('chat', description='Chat operations')
ns_predict_disease = api.namespace('predict-disease', description='Disease prediction operations')
ns_predict_market = api.namespace('predict-market', description='Market prediction operations')

HISTORY_LIMIT = 10

# Define the models for Swagger documentation
message_model = api.model('Message', {
    'message': fields.String(required=True, description='User input message')
})

predict_disease_model = api.model('PredictDisease', {
    'path': fields.String(required=True, description='Path to the crop image'),
    'message': fields.String(required=True, description='User input message')
})

predict_market_model = api.model('PredictMarket', {
    'area': fields.String(required=True, description='Area name'),
    'item': fields.String(required=True, description='Item name'),
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

        return jsonify({'message': intent_response})


@ns_predict_disease.route('/')
class PredictDiseaseResource(Resource):
    @ns_predict_disease.expect(predict_disease_model)
    @ns_predict_disease.response(200, 'Success')
    def get(self):
        """Predicts diseases based on the provided crop image."""
        if 'conversation_history' not in session:
            session['conversation_history'] = CHAT_PROMPT

        crop_img =  request.json.get('path')
        user_input = request.json.get('message')
        
        # model_response = Predict.maize_disease_prediction(TEST_IMG)
        model_response = Predict.maize_disease_prediction(crop_img)
        refined_response = Chat.refine_response(user_input, model_response)
        session['conversation_history'].append({"role": "assistant", "content": refined_response})
        return jsonify({'intent': 'predict maize disease', 'message': refined_response})


@ns_predict_market.route('/')
class PredictMarketResource(Resource):
    @ns_predict_market.expect(predict_market_model)
    @ns_predict_market.response(200, 'Success')
    def get(self):
        """Predicts the market conditions based on user data."""
        if 'conversation_history' not in session:
            session['conversation_history'] = CHAT_PROMPT
        
        user_data = {
            "area": request.json.get("area"),
            "item": request.json.get("item")
        }
        user_input = request.json.get("message")
        
        market_response = Predict.market_prediction(user_data)
        refined_response = Chat.refine_response(user_input, market_response)
        session['conversation_history'].append({"role": "assistant", "content": refined_response})
        return jsonify({'intent': 'predict agriculture market', 'message': refined_response})