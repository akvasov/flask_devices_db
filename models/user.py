"""
This module contains user model definitions to signup a user by adding it's
credentials to 'users' DB or login a user based on already stored credentials.
"""

from flask_login import UserMixin

from db import db

class User(UserMixin, db.Model):
    """Flask-SQLAlchemy DB definition to store users"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(255))

    @classmethod
    def find_by_username(cls, username):
        """A query to find if a user is present into DB"""
        return cls.query.filter_by(username=username).first()