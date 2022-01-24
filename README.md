# Juniper devices inventory project
This python3 Flask project spins up a web application to allow user to populate and consume network devices inventory over web page or API in JSON format.
In this version the app works with Juniper devices leveraging NetConf protocol to connect to devices and gather their inventory.
All users and devices data is stored in PostgreSQL DB.

Flask app utilises next routes:
***
User:
1. '/signup' #user creation ('SIGNUP_PASSWD' is requied to sign up a user)
2. '/login' #user login based on user data stored in PostgreSQL DB 'users' table
3. '/logout' #user logout
***
Devices:
1. '/devices' #provide all network devices inventory stored into PostgreSQL DB 'devices' table
2. '/devices/<device_hostname>' #one defined device inventory stored into PostgreSQL DB 'devices' table
3. '/api/devices' #all network devices inventory stored into PostgreSQL DB 'devices' table in JSON format
4. '/api/devices/<device_hostname>' #one defined device inventory stored into PostgreSQL DB 'devices' table in JSON format
5. '/api/populatedb/<device_filename>' #provide a text file with IP/hostname data to populate devices inventory
6. '/api/add/<device_hostname>' #provide a single hostname to add it into populate network devices inventory
7. '/api/delete/<device_hostname>' #provide a single hostname to remove it into populate network devices inventory
***

## Installation
See 'requirments.txt'

1. CentOS base packages:
```
yum groupinstall “Development Tools”
yum install pip3.6
yum install gcc openssl-devel bzip2-devel libffi-devel python-devel
yum install libxml2-devel libxslt-devel redhat-rpm-config 
```
2. Python modules
```
pip install pipenv
pipenv install flask
pipenv install psycopg2 Flask-SQLAlchemy Flask-WTF flask-login WTForms
pipenv install paramiko junos-eznc
pipenv install python-dotenv
```
3.PostgreSQL installation and setup:
```
yum install postgresql-server postgresql-contrib postgresql-devel postgresql-libs
postgresql-setup initdb
systemctl start postgresql
systemctl enable postgresql
adduser postgreuser
passwd postgreuser
su - postgres
psql
postgres=# CREATE USER postgreuser WITH ENCRYPTED PASSWORD 'xxxx';
postgres=# CREATE DATABASE testDB;
postgres=# GRANT ALL PRIVILEGES ON DATABASE testDB TO postgreuser;
```
***
```
cat /var/lib/pgsql/data/pg_hba.conf | egrep -v "#"
local   all             all                                     peer -------> changed from "ident", required for Flask-SQLAlchemy
host    all             all             127.0.0.1/32            md5 -------> changed from "ident", required for Flask-SQLAlchemy
host    all             all             ::1/128                 ident
```
***
All required PostgreSQL DB tables should be spined up automatically after the first script run.
In case of any issues SQL commands to create them:
```
su - postgreuser
psql testdb
testdb=> CREATE TABLE devices (id serial PRIMARY KEY, hostname VARCHAR (100) UNIQUE NOT NULL, ip VARCHAR (100) UNIQUE NOT NULL, chassis VARCHAR (100) NOT NULL, serialnum VARCHAR (100) UNIQUE NOT NULL, version VARCHAR (100) NOT NULL, type VARCHAR (100) NOT NULL, vendor VARCHAR (100) NOT NULL);
testdb=> CREATE TABLE users (id serial PRIMARY KEY, username VARCHAR (100) UNIQUE NOT NULL, password VARCHAR (100) UNIQUE NOT NULL);
```
## Description


## Implementation
Works with python3.6 or newer
```
]$ python app.py 
```
###.env file variables
```
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
```