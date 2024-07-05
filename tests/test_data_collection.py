import unittest
from unittest.mock import patch, MagicMock
from src.models.data_collection import DataCollection
from src.config.config import Config

class TestDataCollection(unittest.TestCase):

    @patch('src.models.firebase.Firebase.upload_image')
    @patch('src.models.firebase.Firebase.get_farm_info')
    @patch('src.models.firebase.Firebase.add_prediction')
    def test_save_disease_prediction_farm_found(self, mock_add_prediction, mock_get_farm_info, mock_upload_image):
        # Setup mock return values
        mock_upload_image.return_value = 'mocked_img_url'
        mock_get_farm_info.return_value = {
            'farm_name': 'mocked_farm_name',
            'country': 'mocked_country',
            'farming_type': 'mocked_farming_type',
            'land_size': 'mocked_land_size',
            'location': 'mocked_location'
        }

        # Call the method under test
        result = DataCollection.save_disease_prediction('mocked_img', 'mocked_prediction', 'mocked_disease')

        # Assertions
        self.assertEqual(result, {'saved': 'farm found'})
        mock_upload_image.assert_called_once_with('mocked_img')
        mock_get_farm_info.assert_called_once_with(Config.AUTH_TOKEN)
        mock_add_prediction.assert_called_once_with({
            "image": 'mocked_img_url',
            "prediction": 'mocked_prediction',
            "disease": 'mocked_disease',
            'farm_name': 'mocked_farm_name',
            'country': 'mocked_country',
            'farming_type': 'mocked_farming_type',
            'land_size': 'mocked_land_size',
            'location': 'mocked_location'
        }, 'disease-prediction')

    @patch('src.models.firebase.Firebase.upload_image')
    @patch('src.models.firebase.Firebase.get_farm_info')
    @patch('src.models.firebase.Firebase.add_prediction')
    def test_save_disease_prediction_farm_not_found(self, mock_add_prediction, mock_get_farm_info, mock_upload_image):
        # Setup mock return values
        mock_upload_image.return_value = 'mocked_img_url'
        mock_get_farm_info.return_value = {"error": "Farm not found"}

        # Call the method under test
        result = DataCollection.save_disease_prediction('mocked_img', 'mocked_prediction', 'mocked_disease')

        # Assertions
        self.assertEqual(result, {'saved': 'farm not found'})
        mock_upload_image.assert_called_once_with('mocked_img')
        mock_get_farm_info.assert_called_once_with(Config.AUTH_TOKEN)
        mock_add_prediction.assert_called_once_with({
            "image": 'mocked_img_url',
            "prediction": 'mocked_prediction',
            "disease": 'mocked_disease'
        }, 'disease-prediction')

    @patch('src.models.firebase.Firebase.get_farm_info')
    @patch('src.models.firebase.Firebase.add_prediction')
    @patch('src.models.data_collection.datetime')
    def test_save_market_prediction_farm_found(self, mock_datetime, mock_add_prediction, mock_get_farm_info):
        # Setup mock return values
        mock_datetime.now.return_value.strftime.return_value = 'mocked_datetime'
        mock_get_farm_info.return_value = {
            'farm_name': 'mocked_farm_name',
            'country': 'mocked_country',
            'farming_type': 'mocked_farming_type',
            'land_size': 'mocked_land_size',
            'location': 'mocked_location'
        }

        # Call the method under test
        result = DataCollection.save_market_prediction('mocked_area', 'mocked_item', 'mocked_prediction')

        # Assertions
        self.assertEqual(result, {'saved': 'farm found'})
        mock_get_farm_info.assert_called_once_with(Config.AUTH_TOKEN)
        mock_add_prediction.assert_called_once_with({
            "area": 'mocked_area',
            "crop": 'mocked_item',
            "datetime": 'mocked_datetime',
            "prediction": 'mocked_prediction',
            'farm_name': 'mocked_farm_name',
            'country': 'mocked_country',
            'farming_type': 'mocked_farming_type',
            'land_size': 'mocked_land_size',
            'location': 'mocked_location'
        }, 'market-prediction')

    @patch('src.models.firebase.Firebase.get_farm_info')
    @patch('src.models.firebase.Firebase.add_prediction')
    @patch('src.models.data_collection.datetime')
    def test_save_market_prediction_farm_not_found(self, mock_datetime, mock_add_prediction, mock_get_farm_info):
        # Setup mock return values
        mock_datetime.now.return_value.strftime.return_value = 'mocked_datetime'
        mock_get_farm_info.return_value = {"error": "Farm not found"}

        # Call the method under test
        result = DataCollection.save_market_prediction('mocked_area', 'mocked_item', 'mocked_prediction')

        # Assertions
        self.assertEqual(result, {'saved': 'farm not found'})
        mock_get_farm_info.assert_called_once_with(Config.AUTH_TOKEN)
        mock_add_prediction.assert_called_once_with({
            "area": 'mocked_area',
            "crop": 'mocked_item',
            "datetime": 'mocked_datetime',
            "prediction": 'mocked_prediction'
        }, 'market-prediction')

if __name__ == '__main__':
    unittest.main()
