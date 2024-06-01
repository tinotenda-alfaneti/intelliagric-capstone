from src import web_api
from src import database
import json


history_db = database.collection('history')

@web_api.route("/", methods=["GET", "POST"])
def index():
    try:

        
            return json.dumps({"Error":"I am an API, I don't have a front end"})
    except:
        return json.dumps({"error":"Please Enter Valid Data"}, default=TypeError)

#TODO: Instead of saving everything, we give the option to the user, they get to save what they want and then this will be the history
#TODO: Adding a button on each response to be able to save it
"""
Saves a history entry to the database.

This function adds a new document to the 'history_db' database with the following data:
- 'role': 'user'
- 'content': {'answer': "Use fertilizers based on the specific nutrient deficiencies identified in your analysis?", 'topic': "farming"}

If the operation is successful, it returns a JSON response with the message "Data Added Successfully". If there is an error, it returns a JSON response with the message "Please Enter Valid Data".
"""
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