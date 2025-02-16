import unittest
from unittest.mock import patch, MagicMock
import json
import logging
from src.models.notification_service import Notifications
from resources.config import INFOBIP_KEY

class TestNotifications(unittest.TestCase):

    @patch('src.models.notification_service.INFOBIP_KEY', INFOBIP_KEY)
    @patch('src.models.notification_service.http.client.HTTPSConnection')
    def test_send_sms(self, mock_https_connection):
        # Mock the HTTPSConnection instance
        mock_conn = mock_https_connection.return_value
        mock_conn.getresponse.return_value.read.return_value = b'{"messages":[{"status":{"groupId":1,"groupName":"PENDING"}}]}'
        
        Notifications.send_sms("1234567890", "Test message")
        
        mock_https_connection.assert_called_once_with('qy8rj3.api.infobip.com')
        mock_conn.request.assert_called_once_with(
            "POST", "/sms/2/text/advanced", 
            json.dumps({
                "messages": [
                    {
                        "destinations": [{"to": "1234567890"}],
                        "from": "ServiceSMS",
                        "text": "Test message"
                    }
                ]
            }), 
            {
                'Authorization': f'App df35e51f8f298f88e3fa958ba6206f78-77be4bc3-26a1-4861-8cb1-bf02e60188a9',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        logging.info(f'Send SMS Notification: {mock_conn.getresponse.return_value.read.return_value.decode("utf-8")}')

    @patch('src.models.notification_service.INFOBIP_KEY', INFOBIP_KEY)
    @patch('src.models.notification_service.http.client.HTTPSConnection')
    def test_send_email(self, mock_https_connection):
        # Mock the HTTPSConnection instance
        mock_conn = mock_https_connection.return_value
        mock_conn.getresponse.return_value.read.return_value = b'{"messages":[{"status":{"groupId":1,"groupName":"PENDING"}}]}'
        
        Notifications.send_email("test@example.com", "Test Subject", "Test message")
        
        mock_https_connection.assert_called_once_with('qy8rj3.api.infobip.com')
        self.assertTrue(mock_conn.request.called)
        request_args = mock_conn.request.call_args[0]
        
        self.assertEqual(request_args[0], "POST")
        self.assertEqual(request_args[1], "/email/3/send")
        
        # Check headers
        headers = request_args[3]
        self.assertIn('Authorization', headers)
        self.assertIn('Content-Type', headers)
        
        logging.info(f'Send Email Notification: {mock_conn.getresponse.return_value.read.return_value.decode("utf-8")}')
    
    @patch('src.models.notification_service.Notifications.send_sms')
    @patch('src.models.notification_service.Notifications.send_email')
    @patch('src.models.chat.Chat.refine_response')
    def test_send_notifications(self, mock_refine_response, mock_send_email, mock_send_sms):
        alerts = [{'disease': 'disease_1', 'location': 'location_1'}]
        farms = {
            'farm_1': {'location': 'location_1', 'contact': '1234567890', 'email': 'test@example.com'},
            'farm_2': {'location': 'location_2', 'contact': '0987654321', 'email': 'test2@example.com'}
        }

        mock_refine_response.return_value = "Alert: There have been multiple cases of disease_1 detected in your area. Please take necessary precautions."

        Notifications.send_notifications(alerts, farms)

        mock_send_sms.assert_called_once_with('1234567890', "Alert: There have been multiple cases of disease_1 detected in your area. Please take necessary precautions.")
        mock_send_email.assert_called_once_with('test@example.com', "Disease Alert", "Alert: There have been multiple cases of disease_1 detected in your area. Please take necessary precautions.")

if __name__ == '__main__':
    unittest.main()
