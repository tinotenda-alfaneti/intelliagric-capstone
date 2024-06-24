from src import client, database, web_api, db, bucket
import json
import time

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
    def add_farm(farm_data):
        try:
            doc_ref = database.collection('farms').document(farm_data['farmer_id'])
            doc_ref.set(farm_data)
            return json.dumps({"Success": "Farm added successfully"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def link_device_to_user(uid, serial_number, device_type):
        try:
            device_ref = database.collection(f'{device_type}_devices').document(serial_number)
            device = device_ref.get()

            if not device.exists:
                return json.dumps({"error": "Device serial number does not exist"})

            device_data = device.to_dict()
            if 'farmer_id' in device_data and device_data['farmer_id']:
                return json.dumps({"error": "Device already linked to a farmer"})

            device_ref.set({
                'farmer_id': uid,
                'device_type': device_type
            }, merge=True)
            return json.dumps({"Success": "Device linked to user successfully"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def add_device_serial(uid, iot_device_serial):
        try:
            ref = db.reference('iot/')
            all_devices = ref.get()

            if all_devices:
                for key, value in all_devices.items():
                    if value.get('serialnum') == iot_device_serial:
                        return json.dumps({"error": "Serial number already associated with another device"})

            user_ref = ref.child(uid)
            user_ref.set({'serialnum': iot_device_serial})
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
            if not web_api.config["AUTH_TOKEN"]:
                raise Exception("Auth token not found")
            db = database.collection(f'history-{web_api.config["AUTH_TOKEN"]}')
            messages = db.stream()
            message_list = []
            for message in messages:
                message_list.append(message.to_dict())
            return json.dumps({"Success": "Messages retrieved successfully", "messages": message_list})
        except Exception as e:
            return json.dumps({"error": str(e)})
        
    @staticmethod
    def add_prediction(prediction_data, prediction_type):
        try:
            doc_ref = database.collection(prediction_type).add(prediction_data)
            return json.dumps({"Success": "Prediction added successfully"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    @staticmethod
    def upload_image(filename):

        unique_filename = f"img{int(time.time() * 1000)}"
        blob = bucket.blob(unique_filename)
        with open(filename, "rb") as image_file:
            blob.upload_from_file(image_file, content_type='image/png')
        return blob.public_url
    
    @staticmethod
    def delete_img(filename):
        blob = bucket.blob(filename)
        blob.delete()

    @staticmethod
    def save_average_data(avg_data, user_token):
        if user_token != 'none':
            database.collection(f'daily_averages-{user_token}').add(avg_data)

    @staticmethod
    def get_average_data(user_token):
        averages_ref = database.collection(f'daily_averages-{user_token}')
        docs = averages_ref.stream()
        averages = []
        for doc in docs:
            avg_data = doc.to_dict()
            avg_data['id'] = doc.id
            averages.append(avg_data)
        
        return averages
