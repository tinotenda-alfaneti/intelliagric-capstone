import logging
import unittest
from unittest.mock import patch, MagicMock
from src import web_api

# Configure logging
logging.basicConfig(level=logging.DEBUG)
class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.client = web_api.test_client()
        web_api.config['TESTING'] = True

    @patch('src.controllers.auth_controller.verify_id_token')
    @patch('src.controllers.auth_controller.scheduler')
    @patch('src.controllers.auth_controller.save_daily_average')
    @patch('src.controllers.auth_controller.start_transfer')
    def test_login_success(self, mock_start_transfer, mock_save_daily_average, mock_scheduler, mock_verify_id_token):
        # Mock verify_id_token to return a user object
        mock_user = MagicMock()
        mock_user.uid = 'test_uid'
        mock_verify_id_token.return_value = mock_user
        
        mock_scheduler.running = False  # Initial state of scheduler

        response = self.client.post('/auth/login', json={'token': 'valid_token'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200, f"Expected status code 200, got {response.status_code}")
        self.assertEqual(data['success'], 'Login successful')
        mock_verify_id_token.assert_called_once_with('valid_token')
        self.assertEqual(web_api.config["AUTH_TOKEN"], 'valid_token')
        mock_scheduler.add_job.assert_called_once()
        mock_start_transfer.assert_called_once()
        mock_scheduler.start.assert_called_once()
    
    @patch('src.controllers.auth_controller.verify_id_token')
    def test_login_missing_token(self, mock_verify_id_token):
        response = self.client.post('/auth/login', json={})
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Token is missing')
        mock_verify_id_token.assert_not_called()

    @patch('src.controllers.auth_controller.verify_id_token')
    def test_login_invalid_token(self, mock_verify_id_token):
        mock_verify_id_token.return_value = None

        response = self.client.post('/auth/login', json={'token': 'invalid_token'})
        data = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['error'], 'Invalid token')
        mock_verify_id_token.assert_called_once_with('invalid_token')

    def test_logout(self):
        with self.client.session_transaction() as sess:
            sess['some_key'] = 'some_value'

        response = self.client.post('/auth/logout')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], 'Logout successful')
        self.assertEqual(web_api.config["AUTH_TOKEN"], 'none')
        with self.client.session_transaction() as sess:
            self.assertFalse('some_key' in sess)

if __name__ == '__main__':
    unittest.main()
