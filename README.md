# My test API

## Installation
'''
python install Flask
python app.py
'''

## Description


## Implementation
]$ python app.py 

###.env file variables
FLASK_ENV=development #Flask environment (development or production)
FLASK_APP=. #Flask App location
DB_PASSWORD='' #Password for PostgreSQL DB user
DB_PORT='5432' #PostgreSQL DB connection TCP port
DB_USERNAME='' #Username for PostgreSQL DB user
DB_HOST='127.0.0.1' #PostgreSQL DB connection IP
DB_NAME ='' #PostgreSQL DB name
SIGNUP_PASSWD='' #Password to provide for a user to signup for the flasp web app access
FLASK_SECRET_KEY='' # Flask Secret key
J_PASSWD='' # User password to access network devices (system $USER variable used as username)
DEVICES_FILE = '' # File with network devices IP/hostname information to gather info from


### Notes
All required PostgreSQL DB tables should be spined up automatically after the first script run.
In case of any issues SQL commands to create them:
'CREATE TABLE devices (id serial PRIMARY KEY, hostname VARCHAR (100) UNIQUE NOT NULL, ip VARCHAR (100) UNIQUE NOT NULL, chassis VARCHAR (100) NOT NULL, serialnum VARCHAR (100) UNIQUE NOT NULL, version VARCHAR (100) NOT NULL, type VARCHAR (100) NOT NULL, vendor VARCHAR (100) NOT NULL);
CREATE TABLE users (id serial PRIMARY KEY, username VARCHAR (100) UNIQUE NOT NULL, password VARCHAR (100) UNIQUE NOT NULL);'
