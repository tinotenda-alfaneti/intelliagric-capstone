import json
import urllib3
from src.config.db_config import API_KEY


class Authentication:

    def __init__(self):
        pass

    @staticmethod
    def delete_user(uid):
        try:
            request_ref = "https://identitytoolkit.googleapis.com/v1/accounts:delete?key={0}".format(API_KEY)
            headers = {"content-type": "application/json; charset=UTF-8"}
            data = json.dumps({"returnSecureToken": True, "idToken":uid})
            request_object = urllib3.request(method="POST",url=request_ref, headers=headers, body=data)
                  
            return request_object.status
        except:
            return 404

   
            
    