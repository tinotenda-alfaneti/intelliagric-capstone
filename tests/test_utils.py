import unittest
import os
import io
from flask import Flask
from werkzeug.datastructures import FileStorage
from src import ORIGIN_URL, web_api
from src.controllers.utils import UPLOAD_FOLDER

class TestFlaskApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        web_api.config['TESTING'] = True
        cls.client = web_api.test_client()

    def setUp(self):
        # Ensure the uploads folder is clean before each test
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        else:
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)

    def tearDown(self):
        # Clean up any files created during tests
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)

    def test_upload_image_success(self):
        # Create a dummy file
        data = {
            'image': (io.BytesIO(b'my file contents'), 'test_image.jpg')
        }
        response = self.client.post('/upload/image', content_type='multipart/form-data', data=data)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('path', json_data)
        self.assertTrue(os.path.exists(json_data['path']))

    def test_upload_image_no_file(self):
        response = self.client.post('/upload/image', content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data, {"error": "No image part in the request"})

    def test_upload_image_no_filename(self):
        data = {
            'image': (io.BytesIO(b''), '')
        }
        response = self.client.post('/upload/image', content_type='multipart/form-data', data=data)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data, {"error": "No selected file"})

    def test_handle_options(self):
        response = self.client.options('/get_soil_data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), ORIGIN_URL)
        self.assertIn('Authorization', response.headers.get('Access-Control-Allow-Headers'))
        self.assertIn('Content-Type', response.headers.get('Access-Control-Allow-Headers'))
        self.assertIn('POST', response.headers.get('Access-Control-Allow-Methods'))
        self.assertIn('GET', response.headers.get('Access-Control-Allow-Methods'))
        self.assertIn('OPTIONS', response.headers.get('Access-Control-Allow-Methods'))
        self.assertEqual(response.headers.get('Access-Control-Allow-Credentials'), 'true')


if __name__ == '__main__':
    unittest.main()
