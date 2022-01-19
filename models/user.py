from db import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(255))

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()