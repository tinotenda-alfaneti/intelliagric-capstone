import unittest
import json
from unittest.mock import patch, MagicMock
from src.models.firebase import Firebase

class TestFirebase(unittest.TestCase):

    @patch('src.config.db_config.database.collection')
    def test_get_farm_info_farm_found(self, mock_collection):
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'farm_name': 'mock_farm',
            'country': 'mock_country',
            'farming_type': 'mock_farming',
            'land_size': 'mock_land',
            'location': 'mock_location'
        }
        mock_collection.return_value.document.return_value.get.return_value = mock_doc

        result = Firebase.get_farm_info('mock_uuid')
        self.assertEqual(result, {
            'farm_name': 'mock_farm',
            'country': 'mock_country',
            'farming_type': 'mock_farming',
            'land_size': 'mock_land',
            'location': 'mock_location'
        })

    @patch('src.config.db_config.database.collection')
    def test_get_farm_info_farm_not_found(self, mock_collection):
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_collection.return_value.document.return_value.get.return_value = mock_doc

        result = Firebase.get_farm_info('mock_uuid')
        self.assertEqual(result, {'error': 'Farm not found'})

    @patch('src.config.db_config.database.collection')
    def test_add_farm_success(self, mock_collection):
        mock_doc_ref = MagicMock()
        mock_collection.return_value.document.return_value = mock_doc_ref

        result = Firebase.add_farm({'farmer_id': 'mock_farmer'})
        self.assertEqual(result, json.dumps({"Success": "Farm added successfully"}))
        mock_doc_ref.set.assert_called_once_with({'farmer_id': 'mock_farmer'})

    @patch('src.config.db_config.database.collection')
    def test_link_device_to_user_success(self, mock_collection):
        mock_device_ref = MagicMock()
        mock_device = MagicMock()
        mock_device.exists = True
        mock_device.to_dict.return_value = {}

        mock_collection.return_value.document.return_value = mock_device_ref
        mock_device_ref.get.return_value = mock_device

        result = Firebase.link_device_to_user('mock_uid', 'mock_serial', 'iot')
        self.assertEqual(result, json.dumps({"Success": "Device linked to user successfully"}))
        mock_device_ref.set.assert_called_once_with({
            'farmer_id': 'mock_uid',
            'device_type': 'iot'
        }, merge=True)

    @patch('src.config.db_config.database.collection')
    def test_link_device_to_user_device_not_found(self, mock_collection):
        mock_device_ref = MagicMock()
        mock_device = MagicMock()
        mock_device.exists = False

        mock_collection.return_value.document.return_value = mock_device_ref
        mock_device_ref.get.return_value = mock_device

        result = Firebase.link_device_to_user('mock_uid', 'mock_serial', 'iot')
        self.assertEqual(result, json.dumps({"error": "Device serial number does not exist"}))

    @patch('src.config.db_config.database.collection')
    def test_link_device_to_user_device_already_linked(self, mock_collection):
        mock_device_ref = MagicMock()
        mock_device = MagicMock()
        mock_device.exists = True
        mock_device.to_dict.return_value = {'farmer_id': 'another_farmer'}

        mock_collection.return_value.document.return_value = mock_device_ref
        mock_device_ref.get.return_value = mock_device

        result = Firebase.link_device_to_user('mock_uid', 'mock_serial', 'iot')
        self.assertEqual(result, json.dumps({"error": "Device already linked to a farmer"}))

    @patch('src.config.db_config.db.reference')
    def test_add_device_serial_success(self, mock_db_reference):
        mock_ref = MagicMock()
        mock_db_reference.return_value = mock_ref
        mock_ref.get.return_value = None

        result = Firebase.add_device_serial('mock_uid', 'mock_serial')
        self.assertEqual(result, json.dumps({"Success": "Device serial added successfully"}))
        mock_ref.child.return_value.set.assert_called_once_with({'serialnum': 'mock_serial'})
    
    @patch('src.config.db_config.db.reference')
    def test_add_device_serial_already_exists(self, mock_db_reference):
        mock_ref = MagicMock()
        mock_ref.get.return_value = {'some_key': {'serialnum': 'mock_serial'}}

        mock_db_reference.return_value = mock_ref

        result = Firebase.add_device_serial('mock_uid', 'mock_serial')
        self.assertEqual(result, json.dumps({"error": "Serial number already associated with another device"}))

    @patch('src.config.db_config.bucket.blob')
    @patch('builtins.open', new_callable=MagicMock)
    def test_upload_image_success(self, mock_open, mock_blob):
        mock_blob_instance = MagicMock()
        mock_blob.return_value = mock_blob_instance

        mock_blob_instance.upload_from_file.return_value = None
        mock_blob_instance.public_url = 'http://mock_url'

        result = Firebase.upload_image('mock_filename')
        self.assertEqual(result, 'http://mock_url')
        mock_open.assert_called_once_with('mock_filename', 'rb')
        mock_blob_instance.upload_from_file.assert_called_once()

if __name__ == '__main__':
    unittest.main()