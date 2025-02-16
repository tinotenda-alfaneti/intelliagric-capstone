import logging
from flask_restx import Resource, fields
from flask import request, jsonify
from src.config.db_config import database
from src import api
from src.controllers.error_controller import handle_errors
from src.models.chat import Chat

logging.basicConfig(level=logging.DEBUG)

# TODO: add methods interacting with database to firebase module
ns_broadcast = api.namespace('broadcasts', description='Broadcast operations')

broadcast_model = api.model('Broadcast', {
    'disease': fields.String(required=True, description='The disease detected'),
    'location': fields.String(required=True, description='The location of the farms')
})

broadcast_recommendation_model = ns_broadcast.model('BroadcastRecommendation', {
    'diseases': fields.List(fields.String, required=True, description='The diseases detected'),
    'recommendation': fields.String(required=True, description='Recommendation for dealing with the disease')
})

recommendation_request_model = ns_broadcast.model('BroadcastRequest', {
    'diseases': fields.List(fields.String, required=True, description='The diseases detected'),
})

@ns_broadcast.route('/')
class BroadcastList(Resource):
    @handle_errors
    @ns_broadcast.response(200, 'Success', broadcast_model)
    @ns_broadcast.doc(security='Bearer Auth')
    def get(self):
        """List all disease alerts"""
        alerts_ref = database.collection('alerts')
        docs = alerts_ref.stream()
        alerts = [doc.to_dict() for doc in docs]
        logging.debug(alerts)
        return alerts, 200

@ns_broadcast.route('/recommendation')
class BroadcastRecommendation(Resource):
    @handle_errors
    @ns_broadcast.expect(recommendation_request_model)
    @ns_broadcast.response(200, 'Success', broadcast_recommendation_model)
    @ns_broadcast.doc(security='Bearer Auth')
    def post(self):
        """Disease alerts recommendations"""
        diseases = request.json
        if not diseases:
            return jsonify({"error": "Invalid input: No disease provided"})
        
        response = Chat.disease_alerts(diseases)

        logging.debug(response)

        return jsonify({"diseases": diseases, "recommendations":response})


api.add_namespace(ns_broadcast, path='/broadcasts')
api.add_namespace(ns_broadcast, path='/broadcasts/recommendation')
