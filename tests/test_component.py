import unittest
import os
from flask import Flask
from flask_testing import TestCase
from src import web_api

test_img = os.path.dirname(__file__) + "/resources/example.jpg"

class BaseTestCase(TestCase):
    def create_app(self):
        web_api.config['TESTING'] = True
        web_api.config['WTF_CSRF_ENABLED'] = False
        return web_api

class TestChatResource(BaseTestCase):
    def test_chat_message(self):
        response = self.client.post('/chat/', json={'message': 'Hello'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('intent', response.json)

class TestPredictDiseaseResource(BaseTestCase):
    def test_predict_disease(self):
        response = self.client.get('/predict-disease/', json={
            'path': test_img,
            'message': 'What disease does my crop have?'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.json)

if __name__ == '__main__':
    unittest.main()
