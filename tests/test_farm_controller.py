import logging
import unittest
from unittest.mock import patch, MagicMock
from flask_testing import TestCase
from src import web_api, api
from flask_restx import Resource, fields
from src.models.firebase import Firebase
from src.models.utils import API
from src.models.chat import Chat
from resources.config import TOKEN

# Import app components
from flask import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class BaseTestCase(TestCase):
    def create_app(self):
        web_api.config['TESTING'] = True
        web_api.config['WTF_CSRF_ENABLED'] = False
        return web_api

class TestFarmManagementSystem(BaseTestCase):

    @patch('src.controllers.farm_controller.Firebase.add_farm')
    @patch('src.controllers.farm_controller.Firebase.link_device_to_user')
    @patch('src.controllers.farm_controller.Firebase.add_device_serial')
    @patch('src.auth.auth.verify_id_token')
    def test_register_farm_success(self, mock_verify_id_token, mock_add_farm, mock_link_device, mock_add_device_serial):
        # Mock verify_id_token to return a mocked user object
        mock_user = MagicMock()
        mock_user.uid = 'test_user_uid'
        mock_user.email = 'test@example.com'
        mock_verify_id_token.return_value = mock_user

        with self.client:
            response = self.client.post('/farm/register', json={
                'idToken': TOKEN,
                'iotDeviceSerial': 'mocked_iot_serial',
                'droneSerial': 'mocked_drone_serial',
                'country': 'Ghana',
                'farmName': 'Test Farm',
                'landSize': '10 acres',
                'farmingType': 'Organic',
                'contact': '+1234567890'
            }, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type":"application/json"})
            logging.info(response.json)
            self.assertEqual(response.status_code, 200)
            self.assertIn('status', response.json)
            self.assertEqual(response.json['status'], 'success')

            # Verify calls to Firebase methods
            mock_add_farm.assert_called_once()
            mock_link_device.assert_any_call(TOKEN, 'mocked_iot_serial', 'iot')
            mock_link_device.assert_any_call(TOKEN, 'mocked_drone_serial', 'drone')

    @patch('src.controllers.farm_controller.Firebase.get_farm_info')
    @patch('src.models.utils.API.fetch_weather_data')
    @patch.object(Chat, 'farm_overview')
    def test_farm_overview_success(self, mock_farm_overview, mock_fetch_weather_data, mock_get_farm_info):
        # Mock the response from Firebase and API calls
        mock_get_farm_info.return_value = {
            'farmer_id': 'test_user_uid',
            'user_name': 'test_user',
            'user_email': 'test@example.com',
            'iot_device_serial': 'mocked_iot_serial',
            'drone_serial': 'mocked_drone_serial',
            'country': 'Africa',
            'farm_name': 'Test Farm',
            'land_size': '10 acres',
            'farming_type': 'Organic',
            'contact': '+1234567890'
        }
        mock_fetch_weather_data.return_value = 'Clear skies'
        mock_farm_overview.return_value = 'Optimal farming conditions'

        with self.client:
            response = self.client.get('/farm/overview', headers={"Authorization": f"Bearer {TOKEN}"})

            self.assertEqual(response.status_code, 200)
            self.assertIn('response', response.json)
            farm_info = response.json['response']
            self.assertEqual(farm_info['farm_name'], 'Test Farm')
            self.assertEqual(farm_info['country'], 'Africa')
            self.assertEqual(farm_info['farming_type'], 'Organic')
            self.assertEqual(farm_info['land_size'], '10 acres')
            self.assertEqual(farm_info['weather_conditions'], 'Clear skies')
            self.assertEqual(farm_info['recommendations'], 'Optimal farming conditions')

    @patch('src.controllers.farm_controller.Firebase.add_farm')
    @patch('src.auth.auth.verify_id_token')
    def test_register_farm_validation_error(self, mock_verify_id_token, mock_add_farm):
        # Mock verify_id_token to return a mocked user object
        mock_user = MagicMock()
        mock_user.uid = 'test_user_uid'
        mock_user.email = 'test@example.com'
        mock_verify_id_token.return_value = mock_user

        # Missing required field 'landSize' in the request
        with self.client:
            response = self.client.post('/farm/register', json={
                'idToken': 'mocked_id_token',
                'iotDeviceSerial': 'mocked_iot_serial',
                'droneSerial': 'mocked_drone_serial',
                'country': 'Ghana',
                'farmName': 'Test Farm',
                'farmingType': 'Organic',
                'contact': '+1234567890'
            }, headers={"Authorization": f"Bearer {TOKEN}"})

            self.assertEqual(response.status_code, 400)
            self.assertIn('error', response.json)

    @patch('src.controllers.farm_controller.Firebase.get_farm_info')
    def test_farm_overview_validation_error(self, mock_get_farm_info):
        # Simulate Firebase returning None for farm info
        mock_get_farm_info.return_value = None

        with self.client:
            response = self.client.get('/farm/overview', headers={"Authorization": f"Bearer {TOKEN}"})

            self.assertEqual(response.status_code, 400)
            self.assertIn('error', response.json)

if __name__ == '__main__':
    unittest.main()
