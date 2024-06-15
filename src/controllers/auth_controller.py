import json
from src import api
from flask import request, jsonify, session
from flask_restx import Api, Resource, fields
from src.auth.auth import verify_id_token


ns_auth = api.namespace('auth', description='Authentication')

auth_model = api.model('Auth', {
    'token': fields.String(required=True, description='Firebase auth token')
})

@ns_auth.route('/login')
class LoginResource(Resource):
    @ns_auth.expect(auth_model)
    def post(self):
        '''Logging in controller'''
        data = request.json
        token = data.get('token')
        
        if not token:
            response = jsonify({"error": "Token is missing"})
            response.status_code = 400
            return response
        
        decoded_token = verify_id_token(token)
        if not decoded_token:
            response = jsonify({"error": "Invalid token"})
            response.status_code = 401
            return response
        
        session['auth_token'] = token
        session.permanent = True

        response = jsonify({"success": "Login successful"})
        response.status_code = 200
        return response

@ns_auth.route('/logout')
class LogoutResource(Resource):
    def post(self):
        '''Logout controller'''
        session.pop('auth_token', None)
        response = jsonify({"success": "Logout successful"})
        response.status_code = 200
        return response

    
    