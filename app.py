"""
Runs the web API server on localhost at port 5000 in debug mode.
"""
from src import web_api

if __name__ == '__main__':
    web_api.run(host="localhost", port=5000, debug=True)