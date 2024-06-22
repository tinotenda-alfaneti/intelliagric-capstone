import logging
import unittest
from unittest.mock import patch, MagicMock
from flask_testing import TestCase
from flask import json
from src import web_api, api, Resource, fields
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from resources.config import TOKEN


# Import app components
from src.controllers.chat_controller import session

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

class TestEcommerceQuerySystem(BaseTestCase):

    @patch('src.controllers.nl2sql_controller.SQLDatabase')
    @patch('src.controllers.nl2sql_controller.ChatOpenAI')
    @patch('src.controllers.nl2sql_controller.create_sql_query_chain')
    @patch.object(QuerySQLDataBaseTool, 'invoke')
    @patch.object(StrOutputParser, 'invoke')
    def test_ecommerce_query_success(self, mock_sql_database, mock_chat_openai, mock_create_sql_query_chain,
                                     mock_invoke_sql_query_tool, mock_invoke_str_output_parser):
        # Mock instances
        mock_sql_database.return_value = MagicMock()
        mock_chat_openai.return_value = MagicMock()
        mock_create_sql_query_chain.return_value = MagicMock()
        mock_invoke_sql_query_tool.return_value = 'Mocked SQL Result'
        mock_invoke_str_output_parser.return_value = 'Mocked Response'

        with self.client:
            response = self.client.post('/query_ecommerce/', json={'message': 'What are the latest products?'}, headers={"Authorization": f"Bearer {TOKEN}"})
            
            self.assertEqual(response.status_code, 200)
            self.assertIn('response', response.json)
            self.assertEqual(response.json['response'], 'Mocked Response')

            # Verify session history update
            self.assertIn('chat_history', response.json)
            chat_history = response.json['chat_history']
            self.assertIsInstance(chat_history, list)
            self.assertEqual(len(chat_history), 1)
            self.assertEqual(chat_history[0]['role'], 'assistant')
            self.assertIn('response', chat_history[0]['content'])

    @patch('src.controllers.nl2sql_controller.SQLDatabase')
    @patch('src.controllers.nl2sql_controller.ChatOpenAI')
    @patch('src.controllers.nl2sql_controller.create_sql_query_chain')
    @patch.object(QuerySQLDataBaseTool, 'invoke', side_effect=Exception('Database error'))
    def test_ecommerce_query_database_error(self, mock_sql_database, mock_chat_openai, mock_create_sql_query_chain, mock_invoke_sql_query_tool):
        # Mock instances
        mock_sql_database.return_value = MagicMock()
        mock_chat_openai.return_value = MagicMock()
        mock_create_sql_query_chain.return_value = MagicMock()

        with self.client:
            response = self.client.post('/query_ecommerce/', json={'message': 'What are the latest products?'}, headers={"Authorization": f"Bearer {TOKEN}"})
            
            self.assertEqual(response.status_code, 400)
            self.assertIn('error', response.json)
            self.assertEqual(response.json['error'], 'Database error')

if __name__ == '__main__':
    unittest.main()
