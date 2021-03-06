"""
Configuration file for Flask and Flask-SQLAlchemy modules.
All environment variables are stored in local .env file.
"""

import os

from dotenv import load_dotenv

load_dotenv() #load environment variables from .env file

class Config(object):
    db_host = os.environ.get('DB_HOST')
    db_name = os.environ.get('DB_NAME')
    db_password = os.environ.get('DB_PASSWORD')
    db_port = os.environ.get('DB_PORT')
    db_user = os.environ.get('DB_USERNAME')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True