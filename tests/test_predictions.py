import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import requests
import json
import pandas as pd
from src.models.utils import API, DISEASE_MODEL_ENDPOINT, HEADERS, MARKET_MODEL_ENDPOINT, YEAR, crop_yields_data
from src.models.predictions import Predict

class TestPredict(unittest.TestCase):

    @patch('src.models.predictions.requests.post')
    def test_maize_disease_prediction(self, mock_post):
        # Mocking the requests.post response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"label": "Disease A", "score": 0.7},
            {"label": "Disease B", "score": 0.2}
        ]
        mock_post.return_value = mock_response

        with patch('builtins.open', unittest.mock.mock_open(read_data=b"filedata")) as mock_file:
            response = Predict.maize_disease_prediction("dummy_filename")
        
        self.assertEqual(response['disease'], "Disease A")
        self.assertEqual(response['disease_probability'], "0.700")
        mock_post.assert_called_once_with(
            DISEASE_MODEL_ENDPOINT,
            headers=HEADERS,
            data=b"filedata"
        )

    @patch('src.models.predictions.requests.post')
    @patch('src.models.predictions.API.get_yearly_weather_data')
    def test_market_prediction(self, mock_get_weather_data, mock_post):
        # Mocking the weather data retrieval
        mock_get_weather_data.return_value = (25.0, 1000.0)

        # Mocking the requests.post response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'prediction': 150}
        mock_post.return_value = mock_response

        # Mocking the pandas read_csv
        mock_df = pd.DataFrame({
            'Item': ['Wheat', 'Maize', 'Maize'],
            'hg/ha_yield': [3000, 5000, 6000]
        })
        with patch('pandas.read_csv', return_value=mock_df):
            request_data = {
                "area": "Kenya",
                "item": "Maize"
            }
            response = Predict.market_prediction(request_data)

        self.assertEqual(response['supply_prediction'], 150)
        self.assertEqual(response['average_supply'], 5500)
        self.assertEqual(response['crop'], "Maize")
        self.assertEqual(response['country'], "Kenya")
        mock_post.assert_called_once_with(
            MARKET_MODEL_ENDPOINT,
            json={
                "Area": "Kenya",
                "Item": "Maize",
                "average_rain_fall_mm_per_year": 1000.0,
                "avg_temp": 25.0
            }
        )

if __name__ == '__main__':
    unittest.main()

