import logging
import unittest
from unittest.mock import patch, MagicMock
from flask import json, request, session
from src import web_api
from src.controllers.nl2sql_controller import EcommerceQueryResource
from resources.config import TOKEN

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class TestEcommerceQueryResource(unittest.TestCase):

    def setUp(self):
        # Initialize Flask test client
        self.app = web_api
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.client.environ_base['HTTP_AUTHORIZATION'] = f"Bearer {TOKEN}"

    @patch('src.controllers.nl2sql_controller.generate_query')
    @patch('src.controllers.nl2sql_controller.execute_query')
    @patch('src.controllers.nl2sql_controller.rephrase_answer')
    def test_post_success(self, mock_rephrase_answer, mock_execute_query, mock_generate_query):
        # Setup Mocks
        mock_generate_query.invoke.return_value = 'SELECT * FROM employees WHERE department = "Sales";'
        mock_execute_query.invoke.return_value = [{'name': 'John Doe', 'department': 'Sales'}]
        mock_rephrase_answer.invoke.return_value = 'John Doe works in the Sales department.'

        # Mock request data
        with self.app.test_request_context('/query_ecommerce/', method='POST', json={'message': 'Show me all employees in the Sales department'}, headers={"Authorization": f"Bearer {TOKEN}"}):
            # Mock Flask session
            with self.client.session_transaction() as sess:
                sess['conversation_history'] = []

            # Make the POST request
            response = self.client.post('/query_ecommerce/', json={'message': 'Show me all employees in the Sales department'}, headers={"Authorization": f"Bearer {TOKEN}"})
            response_data = response.json

            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertIn('response', response_data)
            self.assertEqual(response_data['response'], 'John Doe works in the Sales department.')
            self.assertIn('chat_history', response_data)
            self.assertEqual(len(response_data['chat_history']), 1)
            self.assertEqual(response_data['chat_history'][0]['content'], 'John Doe works in the Sales department.')


    @patch('src.controllers.nl2sql_controller.generate_query')
    def test_post_no_message(self, mock_generate_query):
        # Mock request data
        with self.app.test_request_context('/query_ecommerce/', method='POST', json={}, headers={"Authorization": f"Bearer {TOKEN}"}):
            # Make the POST request
            response = self.client.post('/query_ecommerce/', json={}, headers={"Authorization": f"Bearer {TOKEN}"})
            response_data = response.json

            # Assertions
            self.assertEqual(response.status_code, 400)
            self.assertIn('error', response_data)
            self.assertEqual(response_data['error'], 'Message is required')


    @patch('src.controllers.nl2sql_controller.generate_query', side_effect=Exception('Mocked exception'))
    def test_post_generate_query_exception(self, mock_generate_query):
        # Mock request data
        with self.app.test_request_context('/query_ecommerce/', method='POST', json={'message': 'Show me all employees in the Sales department'}, headers={"Authorization": f"Bearer {TOKEN}"}):
            # with patch('flask.request.get_json') as mock_get_json:
            with patch('flask.request.get_json', return_value={'message': 'Show me all employees in the Sales department'}):
                # mock_get_json.return_value = {'message': 'Show me all employees in the Sales department'}
                
                # Mock Flask session
                with self.client.session_transaction() as sess:
                    sess['conversation_history'] = []

                # Make the POST request
                response = self.client.post('/query_ecommerce/', json={'message': 'Show me all employees in the Sales department'}, headers={"Authorization": f"Bearer {TOKEN}"})
                response_data = response.get_json()

                # Assertions
                self.assertEqual(response.status_code, 500)
                self.assertIn('error', response_data)
                self.assertEqual(response_data['error'], 'An error occurred while processing your request')

if __name__ == '__main__':
    unittest.main()
