import os
from dotenv import load_dotenv
load_dotenv() #load environment variables from .env file


db_host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')
db_password = os.environ.get('DB_PASSWORD')
db_port = os.environ.get('DB_PORT')
db_user = os.environ.get('DB_USERNAME')

SQLALCHEMY_DATABASE_URI = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
