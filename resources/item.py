from sre_parse import GLOBAL_FLAGS
from flask_restful import Resource,reqparse
from flask_jwt_extended import jwt_required,get_jwt,get_jwt_identity
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help="This field cannot be left blank."
    )
    parser.add_argument('store_id',
        type=int,
        required=True,
        help="Every item needs a store ID."
    )

    @jwt_required() # this will make it required that we have auth before proceeding 
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return{'message': 'Item not found'},404

    @jwt_required(fresh=True)
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400 # 400 is bad request

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": "An error occured inserting the item."}, 500 # internal server error

        return item.json(), 201 #201 created, 202 accepted, but not created
    
    @jwt_required()
    def delete(self, name):
        claims = get_jwt()
        if not claims['is_admin']:
            return {'message' : 'Admin privilege required.'}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        
        return {'message': 'Item deleted'}

    def put(self,name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data) # can use **data to pass all args
        else:
            item.price = data['price']

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.query.all()]
        if user_id:
            return {'items' : items}, 200
        return {
            'items': [item['name'] for item in items],
            'message' : 'more data available if you log in.'
        }, 200
