# import unittest
# from unittest.mock import patch, MagicMock
# from flask import Flask, request, jsonify
# from functools import wraps
# from src.auth.auth import verify_id_token, login_required, login_routine
# from src.config.config import Config

# app = Flask(__name__)

# class TestAuth(unittest.TestCase):

#     @patch('src.auth.auth.auth.get_user')
#     def test_verify_id_token_success(self, mock_get_user):
#         mock_user = MagicMock()
#         mock_get_user.return_value = mock_user

#         user = verify_id_token('valid_token')
#         self.assertEqual(user, mock_user)
#         mock_get_user.assert_called_once_with('valid_token')

#     @patch('src.auth.auth.auth.get_user')
#     def test_verify_id_token_failure(self, mock_get_user):
#         mock_get_user.side_effect = Exception("Invalid token")

#         user = verify_id_token('invalid_token')
#         self.assertIsNone(user)
#         mock_get_user.assert_called_once_with('invalid_token')

#     @patch('src.auth.auth.verify_id_token')
#     def test_login_required_success(self, mock_verify_id_token):
#         mock_verify_id_token.return_value = MagicMock()

#         @app.route('/protected')
#         @login_required
#         def protected():
#             return jsonify({"message": "Success"})

#         with app.test_client() as client:
#             response = client.get('/protected', headers={'Authorization': 'Bearer valid_token'})
#             self.assertEqual(response.status_code, 200)
#             self.assertEqual(response.json, {"message": "Success"})
#             mock_verify_id_token.assert_called_once_with('valid_token')

#     @patch('src.auth.auth.verify_id_token')
#     def test_login_required_missing_auth_header(self, mock_verify_id_token):
#         @app.route('/protected')
#         @login_required
#         def protected():
#             return jsonify({"message": "Success"})

#         with app.test_client() as client:
#             response = client.get('/protected')
#             self.assertEqual(response.status_code, 401)
#             self.assertEqual(response.json, {"error": "Authorization token is missing or invalid"})
#             mock_verify_id_token.assert_not_called()

#     @patch('src.auth.auth.verify_id_token')
#     def test_login_required_invalid_token(self, mock_verify_id_token):
#         mock_verify_id_token.return_value = None

#         @app.route('/protected')
#         @login_required
#         def protected():
#             return jsonify({"message": "Success"})

#         with app.test_client() as client:
#             response = client.get('/protected', headers={'Authorization': 'Bearer invalid_token'})
#             self.assertEqual(response.status_code, 401)
#             self.assertEqual(response.json, {"error": "Invalid token"})
#             mock_verify_id_token.assert_called_once_with('invalid_token')

#     def test_login_routine(self):
#         login_routine('test_token')
#         self.assertEqual(Config.AUTH_TOKEN, 'test_token')


# if __name__ == '__main__':
#     unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from src.auth.auth import verify_id_token, login_required, login_routine
from src.config.config import Config

class TestAuth(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

        @self.app.route('/protected')
        @login_required
        def protected():
            return jsonify({"message": "Success"})
    
    @patch('src.auth.auth.auth.get_user')
    def test_verify_id_token_success(self, mock_get_user):
        mock_user = MagicMock()
        mock_get_user.return_value = mock_user

        user = verify_id_token('valid_token')
        self.assertEqual(user, mock_user)
        mock_get_user.assert_called_once_with('valid_token')

    @patch('src.auth.auth.auth.get_user')
    def test_verify_id_token_failure(self, mock_get_user):
        mock_get_user.side_effect = Exception("Invalid token")

        user = verify_id_token('invalid_token')
        self.assertIsNone(user)
        mock_get_user.assert_called_once_with('invalid_token')

    @patch('src.auth.auth.verify_id_token')
    def test_login_required_success(self, mock_verify_id_token):
        mock_verify_id_token.return_value = MagicMock()

        with self.app.test_client() as client:
            response = client.get('/protected', headers={'Authorization': 'Bearer valid_token'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"message": "Success"})
            mock_verify_id_token.assert_called_once_with('valid_token')

    @patch('src.auth.auth.verify_id_token')
    def test_login_required_missing_auth_header(self, mock_verify_id_token):
        with self.app.test_client() as client:
            response = client.get('/protected')
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json, {"error": "Authorization token is missing or invalid"})
            mock_verify_id_token.assert_not_called()

    @patch('src.auth.auth.verify_id_token')
    def test_login_required_invalid_token(self, mock_verify_id_token):
        mock_verify_id_token.return_value = None

        with self.app.test_client() as client:
            response = client.get('/protected', headers={'Authorization': 'Bearer invalid_token'})
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json, {"error": "Invalid token"})
            mock_verify_id_token.assert_called_once_with('invalid_token')

    def test_login_routine(self):
        login_routine('test_token')
        self.assertEqual(Config.AUTH_TOKEN, 'test_token')

if __name__ == '__main__':
    unittest.main()
