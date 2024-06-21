from flask import request
from firebase_admin import db
from src.auth.auth import verify_id_token
from src import api, database, Resource, fields, web_api
from src.auth.auth import login_required
from src.models.firebase import Firebase
from src.models.utils import API
from src.models.chat import Chat

ns_farm = api.namespace('farm', description='Farm Management endpoint - register and overview')

farm_model = api.model('RegisterFarm', {
    'idToken': fields.String(required=True, description='Firebase ID token'),
    'iotDeviceSerial': fields.String(required=False, description='IoT Device Serial Number'),
    'droneSerial': fields.String(required=False, description='Drone Serial Number'),
    'country': fields.String(required=True, description='Country'),
    'farmName': fields.String(required=True, description='Farm Name'),
    'landSize': fields.String(required=True, description='Land Size'),
    'farmingType': fields.String(required=True, description='Farming Type'),
    'contact': fields.String(required=True, description='Contact'),
})

# Model for the farm overview response
#TODO: Add shop info
farm_overview_model = api.model('FarmOverview', {
    'farm_name': fields.String(required=True, description='The name of the farm'),
    'country': fields.String(required=True, description='The country the farm is located'),
    'farming_type': fields.String(required=True, description='Type of farming'),
    'land_size': fields.String(required=True, description='Size of the land in hectares'),
    'weather_conditions': fields.String(required=True, description='Current weather conditions'),
    'recommendations': fields.String(required=True, description='Recommendations based on current data'),
})

@ns_farm.route('/register')
class RegisterFarm(Resource):
    @login_required
    @ns_farm.expect(farm_model)
    @ns_farm.response(200, 'Success')
    @ns_farm.response(400, 'Validation Error')
    def post(self):
        data = request.json
        id_token = data.get('idToken')
        iot_device_serial = data.get('iotDeviceSerial')
        drone_serial = data.get('droneSerial')
        country = data.get('country')
        contact = data.get('contact')
        farm_name = data.get('farmName')
        land_size = data.get('landSize')
        farming_type = data.get('farmingType')

        try:
            # Verify the ID token
            user = verify_id_token(id_token)
            uid = user.uid
            user_email = user.email
            user_name = user_email.split("@")[0]

            # Save farm data to Firestore
            farm_data = {
                'farmer_id': uid,
                'user_name': user_name,
                'user_email': user_email,
                'iot_device_serial': iot_device_serial,
                'drone_serial': drone_serial,
                'country': country,
                'farm_name': farm_name,
                'land_size': land_size,
                'farming_type': farming_type,
                'contact': contact
            }
            
            Firebase.add_farm(farm_data)
            if iot_device_serial:
                Firebase.link_device_to_user(uid, iot_device_serial, 'iot')
            if drone_serial:
                Firebase.link_device_to_user(uid, drone_serial, 'drone')

            if iot_device_serial:
                Firebase.add_device_serial(uid, iot_device_serial)

            return {'status': 'success'}, 200

        except Exception as e:
            return {'error': str(e)}, 400
        
@ns_farm.route('/overview')
class FarmOverview(Resource):
    @login_required
    @ns_farm.response(200, 'Success', model=farm_overview_model)
    @ns_farm.response(400, 'Validation Error')
    def get(self):

        try:
            farm_info = Firebase.get_farm_info(web_api.config["AUTH_TOKEN"])

            weather_info = API.fetch_weather_data(farm_info['country'])

            farm_info['weather_conditions'] = weather_info

            recommendations = Chat.farm_overview(farm_info)

            farm_info['recommendations'] = recommendations

            return {'response': farm_info}, 200

        except Exception as e:
            return {'error': str(e)}, 400



api.add_namespace(ns_farm, path='/farm/register')
api.add_namespace(ns_farm, path='/farm/overview')