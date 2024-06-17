from flask import request
from firebase_admin import db
from src.auth.auth import verify_id_token
from src import api, database, Resource, fields, web_api
from src.auth.auth import login_required

ns_farm = api.namespace('register-farm', description='Register Farm')

farm_model = api.model('Farm', {
    'idToken': fields.String(required=True, description='Firebase ID token'),
    'iotDeviceSerial': fields.String(required=False, description='IoT Device Serial Number'),
    'droneSerial': fields.String(required=False, description='Drone Serial Number'),
    'country': fields.String(required=True, description='Country'),
    'farmName': fields.String(required=True, description='Farm Name'),
    'landSize': fields.String(required=True, description='Land Size'),
    'farmingType': fields.String(required=True, description='Farming Type'),
    'contact': fields.String(required=True, description='Contact'),
})

@ns_farm.route('/')
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
            database.collection('farms').add(farm_data)

            if iot_device_serial:
                link_device_to_user(uid, iot_device_serial, 'iot')
            if drone_serial:
                link_device_to_user(uid, drone_serial, 'drone')

            if iot_device_serial:
                ref = db.reference(f'iot/{uid}')
                ref.set({'serialnum': iot_device_serial})

            return {'status': 'success'}, 200

        except Exception as e:
            return {'error': str(e)}, 400

def link_device_to_user(uid, serial_number, device_type):
    device_ref = database.collection(f'{device_type}_devices').document(serial_number)
    device_ref.set({
        'farmer_id': uid,
        'device_type': device_type
    }, merge=True)

api.add_namespace(ns_farm, path='/register-farm')