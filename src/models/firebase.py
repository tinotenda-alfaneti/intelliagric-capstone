from src import client, database, web_api, db
import json

class Firebase:

    @staticmethod
    def get_farm_info(uuid):

        farm_doc = database.collection('farms').document(uuid).get()
        
        if farm_doc.exists:
            farm_data = farm_doc.to_dict()

            farm_info = {
                'farm_name': farm_data['farm_name'],
                'country': farm_data['country'],
                'farming_type': farm_data['farming_type'],
                'land_size': farm_data['land_size']
            }

            return farm_info
        else:
            return {'error': 'Farm not found'}

    #TODO: Add error handling  
    @staticmethod
    def link_device_to_user(uid, serial_number, device_type):
        device_ref = database.collection(f'{device_type}_devices').document(serial_number)
        device_ref.set({
            'farmer_id': uid,
            'device_type': device_type
        }, merge=True)

    @staticmethod
    def add_farm(farm_data):

        database.collection('farms').document(farm_data['farmer_id']).add(farm_data)

    @staticmethod
    def add_device_serial(uid, iot_device_serial):
        ref = db.reference(f'iot/{uid}')
        ref.set({'serialnum': iot_device_serial})

    @staticmethod
    def save_chat(message):

        try:
            db = database.collection(f'history-{web_api.config["AUTH_TOKEN"]}')

            db.add(message)

            print(f'Document added with ID: {db[1].id}')
        
            return json.dumps({"Success":"Data Added Successfully"})
        except:
            return json.dumps({"error":"Please Enter Valid Data"}, default=TypeError)




