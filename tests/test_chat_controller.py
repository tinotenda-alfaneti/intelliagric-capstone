import logging
import unittest
from unittest.mock import patch, MagicMock
from flask_testing import TestCase
from src import web_api
from flask import json
from resources.config import TOKEN

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class BaseTestCase(TestCase):
    def create_app(self):
        web_api.config['TESTING'] = True
        web_api.config['WTF_CSRF_ENABLED'] = False
        return web_api

class TestChatSystem(BaseTestCase):

    @patch('src.models.firebase.Firebase.save_chat')
    def test_save_chat_message(self, mock_save_chat):
        # Configure the mock
        mock_save_chat.return_value = json.dumps({"success": "Message saved successfully"})

        with self.client:
            response = self.client.post('/chat/save', json=json.dumps({
                'role': 'user',
                'content': 'Hello',
                'timestamp': '2024-06-21T12:00:00Z'
            }), headers={"Authorization": f"Bearer {TOKEN}"})
            self.assertEqual(response.status_code, 200)
            print(response.get_data(as_text=True))
            response_data = json.loads(response.get_data(as_text=True))
            self.assertIn('success', response_data)
            self.assertEqual(response_data['success'], "Message saved successfully")

    @patch('src.models.firebase.Firebase.retrieve_saved_chats')
    def test_retrieve_saved_chats(self, mock_retrieve_saved_chats):
        # Configure the mock
        mock_retrieve_saved_chats.return_value = json.dumps({
            "success": "Messages retrieved successfully",
            "messages": [
                {'user_id': 'user1', 'message': 'Hello', 'timestamp': '2024-06-21T12:00:00Z'},
                {'user_id': 'user2', 'message': 'Hi', 'timestamp': '2024-06-21T12:05:00Z'}
            ]
        })

        with self.client:
            response = self.client.get('/chat/saved_chats', headers={"Authorization": f"Bearer {TOKEN}"})
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.get_data(as_text=True))
            self.assertIn('success', response_data)
            self.assertIn('messages', response_data)
            self.assertEqual(response_data['success'], "Messages retrieved successfully")
            self.assertIsInstance(response_data['messages'], list)

    @patch('src.models.chat.Chat.get_intent_and_response')
    def test_chat_flow_with_intent_response(self, mock_get_intent_and_response):
        # Configure the mock
        mock_get_intent_and_response.return_value = {"intent": "#General", "response": "This is a mock response"}

        with self.client:
            with self.client.session_transaction() as sess:
                sess['conversation_history'] = [
                    {"role": "user", "content": "Hello"}
                ]

            response = self.client.post('/chat/', json={"message": "Tell me about farming"}, headers={"Authorization": f"Bearer {TOKEN}"})
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.get_data(as_text=True))
            self.assertIn('intent', response_data['response'])
            self.assertEqual(response_data['response']['intent'], "#General")
            self.assertIn('response', response_data['response'])
            self.assertEqual(response_data['response']['response'], "This is a mock response")
            self.assertIn('chat_history', response_data)
            self.assertEqual(len(response_data['chat_history']), 3)  # initial user message, mock response, new user message

if __name__ == '__main__':
    unittest.main()

