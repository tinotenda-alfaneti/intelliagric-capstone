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
            self.assertIn('intent', response.json)
            self.assertEqual(response.json.intent, "#General")
            self.assertIn('response', response.json)
    
    def test_full_chat_flow_market(self):

        with self.client:
            response = self.client.post('/chat/', json={'message': 'Predict future market for maize here in Ghana'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('intent', response.json)
            self.assertIn('area', response.json)
            self.assertIn('crop', response.json)
            self.assertEqual(response.json.intent, "#Predict Agriculture Market")
            self.assertIn('response', response.json)

if __name__ == '__main__':
    unittest.main()
