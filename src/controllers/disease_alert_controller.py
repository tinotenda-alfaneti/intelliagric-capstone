import logging
from flask_restx import Resource, fields
from src.config.db_config import database
from src import api
from src.controllers.error_controller import handle_errors
logging.basicConfig(level=logging.DEBUG)

# TODO: add methods interacting with database to firebase module
ns_broadcast = api.namespace('broadcasts', description='Broadcast operations')

broadcast_model = api.model('Broadcast', {
    'disease': fields.String(required=True, description='The disease detected'),
    'location': fields.String(required=True, description='The location of the farms')
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
        # TODO: Add gpt-3.5 model to get way to deal with the diseases
        alerts = [doc.to_dict() for doc in docs]
        logging.debug(alerts)
        return alerts, 200

api.add_namespace(ns_broadcast, path='/broadcasts')
