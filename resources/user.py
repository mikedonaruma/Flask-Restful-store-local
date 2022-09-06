from flask import jsonify
from flask_restful import Resource, reqparse
import hmac
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    get_jwt_identity, 
    jwt_required,
    get_jwt)
from blocklist import BLOCKLIST
from models.user import UserModel
from werkzeug.security import generate_password_hash, check_password_hash

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
        type=str,
        required=True,
        help="This field cannot be left blank."
    )
_user_parser.add_argument('password',
        type=str,
        required=True,
        help="This field cannot be left blank."
    )

class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message" : "A user with that username already exists"}, 400

        user = UserModel(data['username'],generate_password_hash(data['password']))
        user.save_to_db()

        return {"message": "User created successfully."}, 201

class User(Resource):
    @classmethod
    def get(cls, user_id):
        user  = UserModel.find_by_id(user_id)
        if not user:
            return {'message' : 'User not found'}, 404
        return user.json()

    def delete(cls,user_id):
        user  = UserModel.find_by_id(user_id)
        if not user:
            return {'message' : 'User not found'}, 404

        user.delete_from_db()
        return {'message' : 'User deleted'}, 200

class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from the parser
        data = _user_parser.parse_args()

        # find user in the DatabaseError
        user = UserModel.find_by_username(data['username'])
        
        # this is what the 'authenticate()' function used to do
        if user and check_password_hash(user.password,data['password']):  # check password
            access_token = create_access_token(identity=user.id, fresh=True) # create access token
            refresh_token = create_refresh_token(user.id) # create refresh token (we will look at this later)
            return {  # return items
                'access_token' : access_token,
                'refresh_token' : refresh_token
            }, 200
        elif user:
            return {'message' : 'Invalid credentials'}, 401
        return {'message' : 'Invalid credentials'}, 401

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti'] # jti stands for jwt ID
        BLOCKLIST.add(jti)
        return {'message' : 'Sucessfully logged out.'}, 200


       
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token' : new_token}, 200
