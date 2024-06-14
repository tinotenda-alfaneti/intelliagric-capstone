import unittest
import os
from flask import session
from flask_testing import TestCase
from src import web_api

test_img = os.path.dirname(__file__) + "/resources/example.jpg"

class BaseTestCase(TestCase):
    def create_app(self):
        web_api.config['TESTING'] = True
        web_api.config['WTF_CSRF_ENABLED'] = False
        return web_api

class TestChatSystem(BaseTestCase):
    def test_full_chat_flow(self):
        with self.client:
            response = self.client.post('/chat/', json={'message': 'Hello'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('response', response.json)
            self.assertIn('conversation_history', session)
            
            response = self.client.post('/chat/', json={'message': 'Tell me about farming'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('response', response.json)
            self.assertIn('intent', response.json)
            self.assertEqual(len(session['conversation_history']), 5)

class TestPredictDiseaseSystem(BaseTestCase):
    def test_full_predict_disease_flow(self):
        with self.client:
            response = self.client.get('/predict-disease/', json={
                'path': test_img,
                'message': 'What disease does my crop have?'
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn('message', response.json)
            self.assertIn('conversation_history', session)

if __name__ == '__main__':
    unittest.main()
