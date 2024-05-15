import json
import urllib3
from src import API_KEY
import firebase_admin
from firebase_admin import auth


class Authentication:

    def __init__(self):
        pass
    
    @staticmethod
    def login(email, password):
        request_ref = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={0}".format(API_KEY)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        request_object = urllib3.request(method="POST",url=request_ref, headers=headers, body=data)
        return request_object
    
    @staticmethod
    def signup(email, password):
        try:
            request_ref = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={0}".format(API_KEY)
            headers = {"content-type": "application/json; charset=UTF-8"}
            data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
            request_object = urllib3.request(method="POST",url=request_ref, headers=headers, body=data)
                  
            return request_object.status
        except:
            return 404

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
        
    @staticmethod
    def is_verified(email):
        data = auth.get_user_by_email(email, app=None)
        return data.email_verified

   
            
    