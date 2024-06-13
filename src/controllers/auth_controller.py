import json
from src import web_api
from flask import request

from src.models.authentication import Authentication


@web_api.route('/login', methods =['GET', 'POST'])
def login():
    '''Logging in controller'''

    try:
        if request.method == 'POST' and request.form['email'] and request.form['password']:
            email = request.form['email']
            password = request.form['password']
            user = Authentication.login(email, password)
            
            if user.status == 200:
                
                Authentication.is_verified(email)
                return json.dumps({"Success":"Login Successful"})
            
            else:
                return json.dumps({"error":"Incorrect email / password"}, default=TypeError)
                
        elif request.method == 'POST':
            return json.dumps({"error":"Please Enter Valid Data"}, default=TypeError)
            
    except:
        return json.dumps({"error":"Something went wrong"}, default=TypeError)

    
    