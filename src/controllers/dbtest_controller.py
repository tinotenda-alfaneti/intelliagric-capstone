from src import web_api
from flask import request
from src import database
import json


history_db = database.collection('history')

@web_api.route("/", methods=["GET", "POST"])
def index():
    try:

        
            return json.dumps({"Error":"I am an API, I don't have a front end"})
    except:
        return json.dumps({"error":"Please Enter Valid Data"}, default=TypeError)

@web_api.route("/save_history", methods=["GET", "POST"])
def savehistory():
    try:
            doc_ref = history_db.add({
                'role': 'user',
                'content': {'answer': "Use fertilizers based on the specific nutrient deficiencies identified in your analysis?", 'topic': "farming"}
            })

            print(f'Document added with ID: {doc_ref[1].id}')
        
            return json.dumps({"Success":"Data Added Successfully"})
    except:
        return json.dumps({"error":"Please Enter Valid Data"}, default=TypeError)