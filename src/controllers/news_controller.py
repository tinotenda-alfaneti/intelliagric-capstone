import logging
from src import GNEWS_API_KEY, api
from flask import jsonify
import json
import urllib.request
from flask_restx import fields, Resource

from src.controllers.error_controller import handle_errors

# Configure logging
logging.basicConfig(level=logging.DEBUG)

BASE_URL = "https://gnews.io/api/v4/search"

ns_agriculture_news = api.namespace('agriculture_news', description='Agriculture news operations')

# Define the models for Swagger documentation
news_model = api.model('NewsArticle', {
    'title': fields.String(description='Title of the news article'),
    'description': fields.String(description='Description of the news article'),
    'content': fields.String(description='Content of the news article'),
    'url': fields.String(description='URL of the news article'),
    'image': fields.String(description='Image URL of the news article'),
    'publishedAt': fields.String(description='Publication date of the news article'),
    'source': fields.String(description='Source of the news article')
})

@ns_agriculture_news.route('/')
class AgricultureNewsResource(Resource):
    @handle_errors
    @ns_agriculture_news.response(200, 'Success', [news_model])
    def get(self):
        """Fetches the latest agriculture news in Africa."""
        url = f"{BASE_URL}?q=agriculture+africa&lang=en&country=gh&max=10&apikey={GNEWS_API_KEY}"
        
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode("utf-8"))
                articles = data.get("articles", [])

                articles_data = []
                for article in articles:
                    article_info = {
                        "title": article["title"],
                        "description": article["description"],
                        "content": article["content"],
                        "url": article["url"],
                        "image": article["image"],
                        "publishedAt": article["publishedAt"],
                        "source": article["source"]["name"]
                    }
                    articles_data.append(article_info)
                return jsonify({"articles": articles_data})
        except Exception as e:
            response = jsonify({"error": str(e)})
            response.status_code = 500
            return response

api.add_namespace(ns_agriculture_news, path='/agriculture_news')
