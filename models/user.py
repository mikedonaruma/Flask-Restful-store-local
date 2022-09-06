import sqlite3
from db import db

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(255))

    def __init__(self, username, password):
        # id is a python keyword, so we can't use it as a var, thusly we are using _id 
        # self.id = _id
        self.username = username
        self.password = password

    def json(self):
        return {
            'id' : self.id,
            'username' : self.username,
            'password' : self.password
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod # classmethod allows us to use cls in our function rather than explicetly calling the class User
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first() # SELECT * FROM items WHERE name=name LIMIT 1

    @classmethod # classmethod allows us to use cls in our function rather than explicetly calling the class User
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first() # SELECT * FROM items WHERE name=name LIMIT 1
