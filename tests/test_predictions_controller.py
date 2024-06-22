import unittest
from unittest.mock import patch, MagicMock
from flask_testing import TestCase
from src import web_api
from flask import json, session
from resources.config import TOKEN

class BaseTestCase(TestCase):
    def create_app(self):
        web_api.config['TESTING'] = True
        web_api.config['WTF_CSRF_ENABLED'] = False
        return web_api

class TestPredictionSystem(BaseTestCase):

    @patch('src.models.predictions.Predict.maize_disease_prediction')
    @patch('src.models.chat.Chat.refine_response')
    def test_predict_disease(self, mock_refine_response, mock_maize_disease_prediction):
        # Configure the mocks
        mock_maize_disease_prediction.return_value = "There is an 80% chance of disease."
        mock_refine_response.return_value = {"refined": "disease prediction", "message": "There is an 80% chance that your tomato crop may be infected."}

        with self.client:
            # Make a POST request to predict disease
            response = self.client.post('/predict_disease/', json={
                'path': 'path/to/crop_image.jpg',
                'message': 'What is the condition of my crop?'
            }, headers={"Authorization": f"Bearer {TOKEN}"})

            self.assertEqual(response.status_code, 200)
            self.assertIn('response', response.json)
            self.assertIn('chat_history', response.json)
            self.assertEqual(response.json['response']['intent'], 'predict maize disease')
            self.assertIn('refined', response.json['response']['message'])

            # Check that the mocks were called with the correct arguments
            mock_maize_disease_prediction.assert_called_with('path/to/crop_image.jpg')
            mock_refine_response.assert_called_with('What is the condition of my crop?', 'There is an 80% chance of disease.')

            # Check the number of times the mocks were called
            self.assertEqual(mock_maize_disease_prediction.call_count, 1)
            self.assertEqual(mock_refine_response.call_count, 1)

    @patch('src.models.predictions.Predict.market_prediction')
    @patch('src.models.chat.Chat.refine_response')
    def test_predict_market(self, mock_refine_response, mock_market_prediction):
        # Configure the mocks
        mock_market_prediction.return_value = "The predicted supply of maize is high."
        mock_refine_response.return_value = {"refined": "market prediction", "message": "The predicted supply of maize in Nigeria is high compared to the average of the past 16 years."}

        with self.client:
            # Make a POST request to predict market
            response = self.client.post('/predict_market/', json={
                'area': 'ghana',
                'crop': 'maize',
                'message': 'Predict future market for maize here in Ghana'
            }, headers={"Authorization": f"Bearer {TOKEN}"})

            self.assertEqual(response.status_code, 200)
            self.assertIn('response', response.json)
            self.assertIn('chat_history', response.json)
            self.assertEqual(response.json['response']['intent'], 'predict agriculture market')
            self.assertIn('refined', response.json['response']['message'])

            # Check that the mocks were called with the correct arguments
            mock_market_prediction.assert_called_with({'area': 'Ghana', 'item': 'Maize'})
            mock_refine_response.assert_called_with('Predict future market for maize here in Ghana', 'The predicted supply of maize is high.')

            # Check the number of times the mocks were called
            self.assertEqual(mock_market_prediction.call_count, 1)
            self.assertEqual(mock_refine_response.call_count, 1)

if __name__ == '__main__':
    unittest.main()
