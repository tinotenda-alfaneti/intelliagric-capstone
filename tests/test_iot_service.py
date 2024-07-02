import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import time
import threading
import os
import shutil

from src.models.iot_service import (
    transfer_data, add_data, get_data, clean_old_data, 
    watch_realtime_db, save_daily_average, start_transfer, stop_transfer, check_transfer
)
from src.config.config import Config
import diskcache as dc


class TestIOTService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cache_directory = 'test_cache_directory'
        cls.cache = dc.Cache(cls.cache_directory)
    
    @classmethod
    def tearDownClass(cls):
        cls.cache.clear()
        cls.cache.close()
        shutil.rmtree(cls.cache_directory)

    def setUp(self):
        self.sensor_type = 'mois'
        self.value = 20.5

    def tearDown(self):
        self.cache.clear()

    @patch('src.models.iot_service.cache', new_callable=lambda: dc.Cache('test_cache_directory'))
    def test_add_data(self, mock_cache):
        add_data(self.sensor_type, self.value)
        data = mock_cache.get(self.sensor_type)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['value'], self.value)

    @patch('src.models.iot_service.cache', new_callable=lambda: dc.Cache('test_cache_directory'))
    def test_get_data(self, mock_cache):
        add_data(self.sensor_type, self.value)
        data = get_data(self.sensor_type)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], self.value)

    @patch('src.models.iot_service.cache', new_callable=lambda: dc.Cache('test_cache_directory'))
    def test_clean_old_data(self, mock_cache):
        old_timestamp = time.time() - (25 * 3600)  # older than 24 hours
        mock_cache[self.sensor_type] = [{'timestamp': old_timestamp, 'value': self.value}]
        clean_old_data()
        data = mock_cache.get(self.sensor_type)
        self.assertEqual(len(data), 0)

    @patch('src.models.iot_service.db.reference')
    @patch('src.models.iot_service.cache', new_callable=lambda: dc.Cache('test_cache_directory'))
    def test_watch_realtime_db(self, mock_cache, mock_db_reference):
        mock_reference = MagicMock()
        mock_reference.get.return_value = {self.sensor_type: self.value}
        mock_db_reference.side_effect = [mock_reference, mock_reference]

        watch_realtime_db()
        self.assertEqual(mock_db_reference.call_count, 2)
        mock_db_reference.assert_any_call(f'iot/{Config.AUTH_TOKEN}')
        mock_reference.get.assert_called_once()
        mock_reference.listen.assert_called_once_with(transfer_data)

        data = mock_cache.get(self.sensor_type)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['value'], self.value)

    @patch('src.models.iot_service.Firebase.save_average_data')
    @patch('src.models.iot_service.cache', new_callable=lambda: dc.Cache('test_cache_directory'))
    def test_save_daily_average(self, mock_cache, mock_save_average_data):
        add_data(self.sensor_type, self.value)
        save_daily_average()
        mock_save_average_data.assert_called_once()
        self.assertEqual(mock_cache.get(self.sensor_type), [])

    @patch('src.models.iot_service.watch_realtime_db')
    def test_start_transfer(self, mock_watch_realtime_db):
        start_transfer()
        mock_watch_realtime_db.assert_called_once()

    @patch('src.models.iot_service.Config.AUTH_TOKEN', 'none')
    @patch('src.models.iot_service.logging.info')
    def test_stop_transfer(self, mock_logging_info):
        stop_transfer()
        self.assertEqual(Config.AUTH_TOKEN, 'none')
        mock_logging_info.assert_called_with("Transfer stopped")

    @patch('src.models.iot_service.Config.AUTH_TOKEN', 'valid_token')
    @patch('src.models.iot_service.start_transfer')
    def test_check_transfer_start(self, mock_start_transfer):
        check_transfer()
        mock_start_transfer.assert_called_once()

    @patch('src.models.iot_service.Config.AUTH_TOKEN', 'none')
    @patch('src.models.iot_service.stop_transfer')
    def test_check_transfer_stop(self, mock_stop_transfer):
        check_transfer()
        mock_stop_transfer.assert_called_once()


if __name__ == '__main__':
    unittest.main()
