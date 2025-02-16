import unittest
from unittest.mock import patch, mock_open, MagicMock
from src.models.utils import API, encode_file, encode_file_url, DISEASE_MODEL_ENDPOINT, MARKET_MODEL_ENDPOINT, HEADERS, YEAR, crop_yields_data
import datetime
import requests
import os
import base64
from src import WEATHER_API_KEY

class TestAPI(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data=b'test image data')
    @patch('base64.b64encode')
    def test_encode_file(self, mock_b64encode, mock_open):
        mock_b64encode.return_value.decode.return_value = 'encoded data'
        encoded = encode_file('dummy_path.jpg')
        self.assertEqual(encoded, 'encoded data')
        mock_open.assert_called_once_with('dummy_path.jpg', 'rb')
        mock_b64encode.assert_called_once()

    @patch('requests.get')
    def test_encode_file_url(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'test image data'
        with patch('base64.b64encode') as mock_b64encode:
            mock_b64encode.return_value.decode.return_value = 'encoded data'
            encoded = encode_file_url('http://example.com/image.jpg')
            self.assertEqual(encoded, 'encoded data')
            mock_get.assert_called_once_with('http://example.com/image.jpg')
            mock_b64encode.assert_called_once()

    @patch('requests.get')
    def test_get_country_coordinates(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'coord': {'lon': 10, 'lat': 20}}
        lon, lat = API.get_country_coordinates('Ghana')
        self.assertEqual((lon, lat), (10, 20))
        expected_url = f'https://api.openweathermap.org/data/2.5/weather?q=Ghana&appid={WEATHER_API_KEY}'
        mock_get.assert_called_once_with(expected_url)

    @patch('requests.get')
    def test_get_yearly_weather_data(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "temperature": {"min": 283.15, "max": 293.15},
            "precipitation": {"total": 1.0}
        }

        with patch.object(API, 'get_country_coordinates', return_value=(10, 20)):
            average_temp_year, average_precip_year = API.get_yearly_weather_data(YEAR, 'Ghana')
            self.assertAlmostEqual(average_temp_year, 15.0, places=5)
            self.assertAlmostEqual(average_precip_year, 24.0, places=5)

    @patch('requests.post')
    def test_identify(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {'result': 'mocked response'}
        with patch('src.models.utils.encode_file', return_value='encoded_image'):
            response = API.identify(['dummy_path.jpg'])
            self.assertEqual(response, {'result': 'mocked response'})
            mock_post.assert_called_once()

    @patch('requests.post')
    def test_identify_url(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {'result': 'mocked response'}
        with patch('src.models.utils.encode_file_url', return_value='encoded_image'):
            response = API.identify(['http://example.com/image.jpg'], flag=0)
            self.assertEqual(response, {'result': 'mocked response'})
            mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()

