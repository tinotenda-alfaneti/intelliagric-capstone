import os
import firebase_admin
from firebase_admin import credentials, storage
import cv2
from datetime import datetime
from app import BUCKET

cred = credentials.Certificate("intelliagric.json")
firebase_admin.initialize_app(cred, {'storageBucket': BUCKET})

def upload_images_to_firebase(images):
    bucket = storage.bucket()
    urls = []

    for i, img in enumerate(images):
        img_name = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.jpg"
        cv2.imwrite(img_name, img)
        
        blob = bucket.blob(img_name)
        blob.upload_from_filename(img_name, content_type='image/jpeg')
        urls.append(blob.public_url)
        os.remove(img_name)

    return urls

def get_latest_image_urls():
    from drone_control import perform_flight
    return perform_flight()
