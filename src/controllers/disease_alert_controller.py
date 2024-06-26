from flask_restx import Resource, fields
from src import database, scheduler, api, twilio_client, TWILIO_NUM
from src.controllers.error_controller import handle_errors

#TODO: add methods interacting with database to firebase module
ns_broadcast = api.namespace('broadcasts', description='Broadcast operations')

broadcast_model = api.model('Broadcast', {
    'disease': fields.String(required=True, description='The disease detected'),
    'location': fields.String(required=True, description='The location of the farms')
})

def check_disease_predictions():
    predictions_ref = database.collection('disease-predictions')
    farms_ref = database.collection('farms')

    predictions_docs = predictions_ref.stream()
    farm_docs = farms_ref.stream()

    predictions = [doc.to_dict() for doc in predictions_docs]
    farms = {doc.id: doc.to_dict() for doc in farm_docs}

    disease_counts = {}
    for prediction in predictions:
        disease = prediction['disease']
        farm_id = prediction['farm_id']
        location = farms[farm_id]['location']

        if disease not in disease_counts:
            disease_counts[disease] = {}
        if location not in disease_counts[disease]:
            disease_counts[disease][location] = 0
        
        disease_counts[disease][location] += 1

    alerts = []
    for disease, locations in disease_counts.items():
        for location, count in locations.items():
            if count >= 5:
                alerts.append({'disease': disease, 'location': location})

    send_notifications(alerts, farms)

def send_notifications(alerts, farms):
    for alert in alerts:
        location = alert['location']
        disease = alert['disease']

        affected_farms = [farm for farm in farms.values() if farm['location'] == location]

        for farm in affected_farms:
            contact = farm.get('contact')
            #TODO: Pass the message from GPT-API to make the Alert informative and have recommendations
            message = f"Alert: There have been multiple cases of {disease} detected in your area. Please take necessary precautions."

            if contact:
                twilio_client.messages.create(
                    body=message,
                    from_=TWILIO_NUM, 
                    to=contact
                )

scheduler.add_job(check_disease_predictions, 'cron', hour=0, minute=0)
if scheduler.running == False:
    scheduler.start()

@ns_broadcast.route('/')
class BroadcastList(Resource):
    @handle_errors
    @ns_broadcast.response(200, 'Success', broadcast_model)
    @ns_broadcast.doc(security='Bearer Auth')
    def get(self):
        """List all disease alerts"""
        alerts_ref = database.collection('alerts')
        docs = alerts_ref.stream()
        #TODO: Add gpt-3.5 model to get way to deal with the diseases
        alerts = [doc.to_dict() for doc in docs]
        return alerts, 200

api.add_namespace(ns_broadcast, path='/broadcasts')
