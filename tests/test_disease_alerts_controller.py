import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_restx import Api

from src.controllers.disease_alert_controller import ns_broadcast
from src.config.db_config import database

class TestBroadcastList(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_namespace(ns_broadcast, path='/broadcasts')
        self.client = self.app.test_client()
        self.app.testing = True

    @patch('src.controllers.disease_alert_controller.database')
    def test_get_broadcasts(self, mock_database):
        # Mock the database collection and documents
        mock_alerts_ref = MagicMock()
        mock_doc_1 = MagicMock()
        mock_doc_2 = MagicMock()
        mock_doc_1.to_dict.return_value = {'disease': 'disease_1', 'location': 'location_1'}
        mock_doc_2.to_dict.return_value = {'disease': 'disease_2', 'location': 'location_2'}
        mock_alerts_ref.stream.return_value = [mock_doc_1, mock_doc_2]
        mock_database.collection.return_value = mock_alerts_ref

        response = self.client.get('/broadcasts/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [
            {'disease': 'disease_1', 'location': 'location_1'},
            {'disease': 'disease_2', 'location': 'location_2'}
        ])
        
    @patch('src.controllers.disease_alert_controller.database')
    def test_get_broadcasts_empty(self, mock_database):
        # Mock the database collection with no documents
        mock_alerts_ref = MagicMock()
        mock_alerts_ref.stream.return_value = []
        mock_database.collection.return_value = mock_alerts_ref

        response = self.client.get('/broadcasts/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

if __name__ == '__main__':
    unittest.main()
