from src import web_api, GNEWS_API_KEY
from flask import jsonify
import json
import urllib.request

BASE_URL = "https://gnews.io/api/v4/search"

@web_api.route('/agriculture-news', methods=['GET'])
def get_agriculture_news():
    url = f"{BASE_URL}?q=agriculture+africa&lang=en&country=gh&max=10&apikey={GNEWS_API_KEY}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
            articles = data.get("articles", [])

            # Collecting article data
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
        return jsonify({"error": str(e)}), 500