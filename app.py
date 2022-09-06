from datetime import timedelta
from db import db
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from blocklist import BLOCKLIST


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800) # config JWT to expire within half an hour
app.secret_key = 'jose' # this needs to be secret, and it should be secure, aka long and complicated
api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1: # instead of hard-coding, this should be read froma config file or a database value
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_headers,jwt_payload):
    return jwt_payload['jti'] in BLOCKLIST

@jwt.expired_token_loader
def expired_token_callback(jwt_headers,jwt_payload):
    return jsonify({
        'message': 'The token has expired.',
        'error':'token_expired'
    }),401

@jwt.invalid_token_loader
def invalid_token_callback(jwt_headers,jwt_payload):
    return jsonify({
        'message': 'Signature verification failed.',
        'error':'invalid_token'
    }),401

@jwt.unauthorized_loader
def missing_token_callback(jwt_headers,jwt_payload):
    return jsonify({
        'message': 'Request does not contain an access token.',
        'error':'authorization_required'
    }),401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_headers,jwt_payload):
    return jsonify({
        'message': 'The token is not fresh.',
        'error':'fresh_token_required'
    }),401

@jwt.revoked_token_loader
def invalid_token_callback(jwt_headers,jwt_payload):
    return jsonify({
        'message': 'The token has been revoked',
        'error':'token_revoked'
    }),401

api.add_resource(Item, '/item/<string:name>')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
