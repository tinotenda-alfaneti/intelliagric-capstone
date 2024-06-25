import json
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from src import web_api

class AgricultureNewsResourceTestCase(unittest.TestCase):
    def setUp(self):
        self.client = web_api.test_client()
        web_api.config['TESTING'] = True
    @patch('src.controllers.news_controller.urllib.request.urlopen')
    def test_get_agriculture_news_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "articles": [
                {
                    "title": "Agriculture News 1",
                    "description": "Description 1",
                    "content": "Content 1",
                    "url": "http://example.com/news1",
                    "image": "http://example.com/image1.jpg",
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "source": {"name": "Source 1"}
                },
                {
                    "title": "Agriculture News 2",
                    "description": "Description 2",
                    "content": "Content 2",
                    "url": "http://example.com/news2",
                    "image": "http://example.com/image2.jpg",
                    "publishedAt": "2023-01-02T00:00:00Z",
                    "source": {"name": "Source 2"}
                }
            ]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value.read.return_value = mock_response.read()

        response = self.client.get('/agriculture_news/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("articles", response.json)
        self.assertEqual(len(response.json["articles"]), 2)

    @patch('src.controllers.news_controller.urllib.request.urlopen')
    def test_get_agriculture_news_error(self, mock_urlopen):
        # Simulate an exception being raised
        mock_urlopen.side_effect = Exception("Failed to fetch news")

        # Call the endpoint using the test client
        response = self.client.get('/agriculture_news/')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Failed to fetch news")
if __name__ == '__main__':
    unittest.main()