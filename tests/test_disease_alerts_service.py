import unittest
from unittest.mock import patch, MagicMock
from src.models.disease_alerts_service import DiseaseAlerts

class TestDiseaseAlerts(unittest.TestCase):
    
    @patch('src.models.notification_service.Notifications.send_notifications')
    @patch('src.config.db_config.database.collection')
    def test_check_disease_predictions(self, mock_db_collection, mock_send_notifications):
        # Mock the Firestore collections
        mock_predictions_ref = MagicMock()
        mock_farms_ref = MagicMock()
        mock_db_collection.side_effect = lambda collection_name: {
            'disease-predictions': mock_predictions_ref,
            'farms': mock_farms_ref
        }[collection_name]

        # Mock prediction documents
        mock_predictions_ref.stream.return_value = [
            MagicMock(to_dict=lambda: {'disease': 'disease_1', 'farm_id': 'farm_1'}),
            MagicMock(to_dict=lambda: {'disease': 'disease_1', 'farm_id': 'farm_2'}),
            MagicMock(to_dict=lambda: {'disease': 'disease_1', 'farm_id': 'farm_1'}),
            MagicMock(to_dict=lambda: {'disease': 'disease_1', 'farm_id': 'farm_3'}),
            MagicMock(to_dict=lambda: {'disease': 'disease_1', 'farm_id': 'farm_1'}),
            MagicMock(to_dict=lambda: {'disease': 'disease_1', 'farm_id': 'farm_1'}),
        ]

        # Mock farm documents
        mock_farms_ref.stream.return_value = [
            MagicMock(id='farm_1', to_dict=lambda: {'location': 'location_1'}),
            MagicMock(id='farm_2', to_dict=lambda: {'location': 'location_1'}),
            MagicMock(id='farm_3', to_dict=lambda: {'location': 'location_1'}),
        ]

        # Call the method under test
        DiseaseAlerts.check_disease_predictions()

        # Assert that send_notifications was called with the correct arguments
        expected_alerts = [{'disease': 'disease_1', 'location': 'location_1'}]
        mock_send_notifications.assert_called_once_with(expected_alerts, {
            'farm_1': {'location': 'location_1'},
            'farm_2': {'location': 'location_1'},
            'farm_3': {'location': 'location_1'}
        })

if __name__ == '__main__':
    unittest.main()
