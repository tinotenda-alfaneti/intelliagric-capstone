from src import web_api, api, fields, Resource
import json
import numpy as np
from flask import request, session, jsonify
from src.models.predictions import Predict
from src.models.chat import CHAT_PROMPT
from src.models.chat import Chat


ns_predict_disease = api.namespace('predict-disease', description='Disease prediction operations')
ns_predict_market = api.namespace('predict-market', description='Market prediction operations')


predict_disease_model = api.model('PredictDisease', {
    'path': fields.String(required=True, description='Path to the crop image'),
    'message': fields.String(required=True, description='User input message')
})

predict_market_model = api.model('PredictMarket', {
    'area': fields.String(required=True, description='Area name'),
    'item': fields.String(required=True, description='Item name'),
    'message': fields.String(required=True, description='User input message')
})

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

        # refined response structure:  {"refined": "disease prediction", "message": "There is an 80% chance that your tomato crop may"}
        session['conversation_history'].append({"role": "assistant", "content": refined_response})
        final_response = {'intent': 'predict maize disease', 'message': refined_response}
        return jsonify({'response': final_response, 'chat_history': session['conversation_history']})


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

        # refined response structure: {"refined": "market prediction", "message": "The predicted supply of maize in Nigeria is high compared to the average of the past 16 years."}
        session['conversation_history'].append({"role": "assistant", "content": refined_response})
        final_response = {'intent': 'predict agriculture market', 'message': refined_response}
        return jsonify({'response': final_response, 'chat_history': session['conversation_history']})

api.add_namespace(ns_predict_disease, path='/predict-disease')
api.add_namespace(ns_predict_market, path='/predict-market')  