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

    @staticmethod
    def link_device_to_user(uid, serial_number, device_type):
        try:
            device_ref = database.collection(f'{device_type}_devices').document(serial_number)
            device_ref.set({
                'farmer_id': uid,
                'device_type': device_type
            }, merge=True)
            return json.dumps({"Success": "Device linked to user successfully"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    @staticmethod
    def add_farm(farm_data):
        try:
            doc_ref = database.collection('farms').document(farm_data['farmer_id'])
            doc_ref.set(farm_data)
            return json.dumps({"Success": "Farm added successfully"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    @staticmethod
    def add_device_serial(uid, iot_device_serial):
        try:
            ref = db.reference(f'iot/{uid}')
            ref.set({'serialnum': iot_device_serial})
            return json.dumps({"Success": "Device serial added successfully"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def save_chat(message):
        try:
            db = database.collection(f'history-{web_api.config["AUTH_TOKEN"]}')
            doc_ref = db.add(message)
            print(f'Document added with ID: {doc_ref.id}')
            return json.dumps({"Success": "Data added successfully"})
        except Exception as e:
            return json.dumps({"error": str(e)})
        
    @staticmethod
    def retrieve_saved_chats():
        try:
            db = database.collection(f'history-{web_api.config["AUTH_TOKEN"]}')
            messages = db.stream()
            message_list = []
            for message in messages:
                message_list.append(message.to_dict())
            return json.dumps({"Success": "Messages retrieved successfully", "messages": message_list})
        except Exception as e:
            return json.dumps({"error": str(e)})



