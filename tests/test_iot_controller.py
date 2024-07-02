import logging
import unittest
from unittest.mock import patch, MagicMock
from flask_testing import TestCase
from src import web_api, api
from src.config.db_config import database
from flask_restx import  Resource, fields
from src.models.chat import Chat
from src.auth.auth import login_required
from src.models.iot_service import cache, data_lock, save_daily_average, watch_realtime_db, add_data
from resources.config import TOKEN

# Import app components
from flask import json, session

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class BaseTestCase(TestCase):
    def create_app(self):
        web_api.config['TESTING'] = True
        web_api.config['WTF_CSRF_ENABLED'] = False
        return web_api
    
    def setUp(self):
        self.client = self.app.test_client()
        self.client.environ_base['HTTP_AUTHORIZATION'] = f"Bearer {TOKEN}"

class TestSoilDataSystem(BaseTestCase):

    @patch('requests.get')
    @patch.object(Chat, 'soil_analysis')
    def test_soil_analysis_resource(self, mock_soil_analysis, mock_requests_get):
        # Mock the response from 'get-soil-data' endpoint
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            "mois": 30.5,
            "npk": "10-10-10",
            "temp": 25.0,
            "ph": 6.5
        }
        
        # Mock the soil analysis response
        mock_soil_analysis.return_value = "Healthy soil with optimal conditions for crop growth."

        with self.client:
            response = self.client.get('/soil_analysis/', headers={"Authorization": f"Bearer {TOKEN}"})
            self.assertEqual(response.status_code, 200)
            self.assertIn('analysis', response.json)
            self.assertEqual(response.json['analysis'], "Healthy soil with optimal conditions for crop growth.")

            # Check that requests.get was called with the correct URL
            mock_requests_get.assert_called_once_with(f'http://localhost//get_soil_data', headers={"Authorization": f"Bearer {TOKEN}"})

    @patch('requests.get')
    def test_soil_data_resource(self, mock_requests_get):
        
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = json.dumps({
            "mois": 30.5,
            "npk": "10-10-10",
            "temp": 25.0,
            "ph": 6.5
        })

        add_data('mois', 30.5)
        add_data('npk', "10-10-10")
        add_data('temp', 25.0)
        add_data('ph', 6.5)

        with self.client:
            response = self.client.get('/get_soil_data/', headers={"Authorization": f"Bearer {TOKEN}"})
            self.assertEqual(response.status_code, 200)
            self.assertIn('mois', response.json)
            self.assertEqual(response.json['mois'], 30.5)
            self.assertIn('npk', response.json)
            self.assertEqual(response.json['npk'], "10-10-10")
            self.assertIn('temp', response.json)
            self.assertEqual(response.json['temp'], 25.0)
            self.assertIn('ph', response.json)
            self.assertEqual(response.json['ph'], 6.5)


    @patch('src.scheduler')
    @patch('src.models.firebase.database.collection')
    def test_save_daily_average_job(self, mock_database_collection, mock_scheduler):
        # Mocking the scheduler and datetime to simulate midnight execution
        mock_scheduler.running = True
        mock_scheduler.atexit.register = lambda func: func()
        mock_scheduler.get_jobs.return_value = []
        
        # Mock the database collection and its methods
        mock_database_collection_instance = MagicMock()
        mock_database_collection.return_value = mock_database_collection_instance
        
        # Set accumulated data for testing
        add_data('mois', 25.0)
        add_data('npk', "5-5-5")
        add_data('temp', 20.0)
        add_data('ph', 6.5)
        add_data('mois', 30.0)
        add_data('temp', 22.0)
        add_data('ph', 6.0)
        add_data('mois', 35.0)
        add_data('temp', 25.0)
        add_data('ph', 7.0)

        with self.client:
            # Call the save_daily_average function directly for testing
            save_daily_average()

            # Check that daily averages were saved to Firestore
            self.assertEqual(mock_database_collection.call_count, 1)
            self.assertEqual(mock_database_collection_instance.add.call_count, 1)

            # Check the content of the saved document
            saved_data = mock_database_collection_instance.add.call_args[0][0]
            self.assertIn('mois', saved_data)
            self.assertIn('temp', saved_data)
            self.assertIn('ph', saved_data)


if __name__ == '__main__':
    unittest.main()
