
# import unittest
# from unittest.mock import patch, MagicMock
# from functools import wraps
# from flask import Flask, jsonify, session
# import logging

# from src.controllers.error_controller import handle_errors, InvalidDiseasePredictionError

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)

# # A mock Flask app for testing
# app = Flask(__name__)
# app.secret_key = 'test_secret_key'

# class TestHandleErrors(unittest.TestCase):

#     def setUp(self):
#         self.app = app.test_client()
#         self.app.testing = True

#     @patch('src.controllers.error_controller.session', dict())
#     @patch('src.controllers.error_controller.logging')
#     def test_invalid_disease_prediction_error(self, mock_logging):
#         @handle_errors
#         def mock_function():
#             raise InvalidDiseasePredictionError("Invalid disease prediction response: expected JSON but got a string.")

#         with app.test_request_context():
#             response = mock_function()

#             self.assertEqual(response.status_code, 500)
#             self.assertIn("Oops so sorry, I had an issue during the prediction", response.json['response'])
#             self.assertIn({"role": "assistant", "content": "Oops so sorry, I had an issue during the prediction, please kindly wait for a few seconds and try me again"}, response.json['chat_history'])
#             # mock_logging.exception.assert_called_once_with('Server Error: %s', InvalidDiseasePredictionError("Invalid disease prediction response: expected JSON but got a string."))

#     @patch('src.controllers.error_controller.session', dict())
#     @patch('src.controllers.error_controller.logging')
#     def test_general_exception(self, mock_logging):
#         @handle_errors
#         def mock_function():
#             raise Exception("General error")

#         with app.test_request_context():
#             response = mock_function()

#             self.assertEqual(response.status_code, 500)
#             self.assertIn("Sorry, I am having technical issues please try again in a moment", response.json['response'])
#             self.assertIn({"role": "assistant", "content": "Sorry, I am having technical issues please try again in a moment"}, response.json['chat_history'])
#             # mock_logging.exception.assert_called_once_with('Server Error: %s', Exception("General error"))

#     @patch('src.controllers.error_controller.session', dict())
#     def test_successful_function(self):
#         @handle_errors
#         def mock_function():
#             return jsonify({"response": "Success"}), 200

#         with app.test_request_context():
#             response, status_code = mock_function()

#             self.assertEqual(status_code, 200)
#             self.assertEqual(response.json['response'], "Success")

# if __name__ == '__main__':
#     unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from functools import wraps
from flask import Flask, jsonify, session
import logging

from src.controllers.error_controller import handle_errors, InvalidDiseasePredictionError

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# A mock Flask app for testing
app = Flask(__name__)
app.secret_key = 'test_secret_key'

class TestHandleErrors(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('src.controllers.error_controller.session', dict())
    @patch('src.controllers.error_controller.logging')
    def test_invalid_disease_prediction_error(self, mock_logging):
        @handle_errors
        def mock_function():
            raise InvalidDiseasePredictionError()

        with app.test_request_context():
            response = mock_function()
            status_code = response.status_code if isinstance(response, app.response_class) else response[1]

            self.assertEqual(status_code, 500)
            self.assertIn("Oops so sorry, I had an issue during the prediction", response.json['response'])
            self.assertIn({"role": "assistant", "content": "Oops so sorry, I had an issue during the prediction, please kindly wait for a few seconds and try me again"}, response.json['chat_history'])
            mock_logging.exception.assert_called_once()
            self.assertIn('Server Error: %s', mock_logging.exception.call_args[0])
            self.assertIsInstance(mock_logging.exception.call_args[0][1], InvalidDiseasePredictionError)

    @patch('src.controllers.error_controller.session', dict())
    @patch('src.controllers.error_controller.logging')
    def test_general_exception(self, mock_logging):
        @handle_errors
        def mock_function():
            raise Exception("General error")

        with app.test_request_context():
            response = mock_function()
            status_code = response.status_code if isinstance(response, app.response_class) else response[1]

            self.assertEqual(status_code, 500)
            self.assertIn("Sorry, I am having technical issues please try again in a moment", response.json['response'])
            self.assertIn({"role": "assistant", "content": "Sorry, I am having technical issues please try again in a moment"}, response.json['chat_history'])
            mock_logging.exception.assert_called_once()
            self.assertIn('Server Error: %s', mock_logging.exception.call_args[0])
            self.assertIsInstance(mock_logging.exception.call_args[0][1], Exception)

    @patch('src.controllers.error_controller.session', dict())
    def test_successful_function(self):
        @handle_errors
        def mock_function():
            return jsonify({"response": "Success"}), 200

        with app.test_request_context():
            response, status_code = mock_function()

            self.assertEqual(status_code, 200)
            self.assertEqual(response.json['response'], "Success")

if __name__ == '__main__':
    unittest.main()
