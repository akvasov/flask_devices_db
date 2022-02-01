"""
This python3 Flask app spins up a web application to allow user to populate
and consume network devices inventory over web page or API in JSON format.
In this version the app works with Juniper devices leveraging NetConf protocol
to connect to devices and gather their inventory.
All users and devices data is stored in PostgreSQL DB.
"""
import os
import asyncio

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, url_for,\
                  jsonify, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from jnpr.junos.exception import ConnectError as jnpr_ConnectError
from sqlalchemy.orm import exc
from jnpr.junos.exception import ConnectError, ProbeError, ConfigLoadError

from models.files import FileParcer
from models.login_forms import LoginForm, SignUPForm
from models.device import Device, DeviceJuniper
from models.user import User


def conn_and_populate_db(ip):
    """
    This is a task method for asyncio to connect to a device, gather inventory data
    and populate the DB
    :return Status of the inventory collection based on device reachability
    or presence into DB:
        * Failure to connect => 'status': 'Connection failure'
        * Device is already into DB => 'status': 'Present in DB'
        * Device is successfully added into DB => 'status': 'Success'

    This function is defined outside of Flask App definition, so to access Flask
    dependent methods like SQLAlchemy we need to provide app_context().
    """
    try:
        device_data = DeviceJuniper.dev_output_to_dict(ip)
    except (ConnectError, ProbeError, ConfigLoadError) as e:
        print('Failed to connect to {} with error {}'.format(ip, e))
        return {'status': 'Connection failure', 'device': (ip,)}

    with app.app_context():
        if Device.find_by_hostname(device_data['hostname']):
            print('{} device is present in DB'.format(device_data['hostname']))
            return {'status': 'Present in DB', 'device': (ip, device_data['hostname'])}

    with app.app_context():
        db.session.add(Device(**device_data))
        db.session.commit()
        print('{} device has been added into DB'.format(device_data['hostname']))
        return {'status': 'Success', 'device': (ip, device_data['hostname'])}


async def worker(ip, results):
    """Worker function for asyncio to put tasks into an executor loop """
    loop = asyncio.get_event_loop()
    future_result = loop.run_in_executor(None, conn_and_populate_db, ip)
    result = await future_result
    if result['status'] == 'Success':
        results['success'].append(result['device'])
    elif result['status'] == 'Present in DB':
        results['Present in DB'].append(result['device'])
    elif result['status'] == 'Connection failure':
        results['Connection failure'].append(result['device'])


async def distribute_work(ip_list, results):
    """Divide up work into batches and collect final results """
    tasks = []
    for ip in ip_list:
        task = asyncio.create_task(worker(ip, results))
        tasks.append(task)
    await asyncio.gather(*tasks)


def concurrent_add_devices(ip_list):
    """Asyncio run method for distributed workers returning finale results for
    parallel tasks execution"""
    results = {"success": [], "Present in DB": [], "Connection failure": []}
    asyncio.run(distribute_work(ip_list, results))
    return results


def create_app():
    """Flask app function returning itself"""
    load_dotenv() #Loading all env variables from .env file

    app = Flask(__name__)
    app.config.from_object("config.Config") #Flask app configuration file
    db.init_app(app)
    
    login_manager = LoginManager() #User session management from Flask
    login_manager.init_app(app)
    login_manager.login_view = 'login' #Web page "login.html" for user login

    @app.before_first_request
    def create_tables():
        """Create PostgreSQL DB tables before user makes any requests"""
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        """Callback to return a user object by user_id"""
        return User.query.get(int(user_id))

    def return_to_index(status):
        """
        Function to provide user with a status of request shown
         on 'index.html' page
        """
        return render_template('index.html', status=status)

    @app.errorhandler(404)
    def page_not_found(e):
        """Render a page for HTML 404 status"""
        return render_template('404.html'), 404

    @app.route('/')
    def index():
        """Render a landing page 'index.html' for user App request"""
        return return_to_index('')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        """App route to signup a user based on WTForms custom SignUPForm"""
        form = SignUPForm()
        act_passwd = os.environ.get('SIGNUP_PASSWD')
        if form.validate_on_submit(): #parse form data after user hits 'Submit'
            if act_passwd == form.act_passwd.data:
                hashed_password = generate_password_hash(form.password.data,
                                                         method='sha256')
                db.session.add(User(username=form.username.data,
                                    password=hashed_password))
                db.session.commit()
                return return_to_index('The user has been created. Log in please!')
            else:
                return return_to_index('Error. The SIGNUP activation password is wrong')
        return render_template('signup.html', form=form)

    @app.route('/login', methods=['GET','POST'])
    def login():
        """App route to login a user based on WTForms custom LoginForm"""
        form = LoginForm()
        if form.validate_on_submit(): #parse form data after user hits 'Submit'
            try:
                user = User.find_by_username(form.username.data)
            except exc.NoResultFound:
                return return_to_index('This user does not exist. Sign UP!')
            if user:
                if check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    """
                    Redirect user to 'devices_index.html' upon successful login
                    """
                    return redirect(url_for('devices'))
            return return_to_index('Invalid username or password')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required #User loging is requred for logout
    def logout():
        """App route to logout a user"""
        logout_user()
        return return_to_index('The user has been logged out')

    @app.route('/devices')
    @login_required #User loging is requred to use this App route
    def devices():
        """App route to provide all inventory data onto 'devices_index.html'"""
        devices = Device.query.order_by(Device.type).all()
        return render_template('devices_index.html', devices=devices)

    @app.route('/devices/<device_hostname>')
    @login_required #User loging is requred to use this App route
    def devices_show(device_hostname):
        """App route to provide defined device data onto 'devices_show.html'"""
        try:
            device = Device.find_by_hostname(device_hostname)
            return render_template('devices_show.html', device=device)
        except exc.NoResultFound:
            abort(404)

    @app.route('/api/devices')
    def api_devices_all():
        """GET Method to provide all inventory data in JSON"""
        devices = Device.query.all()
        return jsonify([device.to_json() for device in devices])

    @app.route('/api/devices/<device_hostname>')
    def api_devices_show(device_hostname):
        """GET Method to provide defined device data in JSON"""
        if request.method == 'GET':
            try:
                device = Device.find_by_hostname(device_hostname)
                return jsonify(device.to_json())
            except exc.NoResultFound:
                return jsonify({'error': 'Device not found'}), 404

    @app.route('/api/populatedb/<device_filename>')
    def api_populatedb(device_filename):
        """
        GET Method to populate inventory based on devices IP/hostname data
        in the defined text file
        """
        result = concurrent_add_devices(FileParcer.parse_device_file(device_filename))
        return jsonify({'status': 'DB update status {}'.
                       format(result)}), 200

    @app.route('/api/delete/<device_hostname>', methods=['DELETE'])
    def api_delete_entry(device_hostname):
        """DELETE Method to delete defined device from the inventory"""
        device = Device.find_by_hostname(device_hostname)
        if device:
            db.session.delete(device)
            db.session.commit()
            return jsonify({'status': 'DB entry was cleared for {}'.
                           format(device_hostname)}), 200
        else:
            return jsonify({'error': 'Device is NOT present in DB'}), 404

    @app.route('/api/add/<device_hostname>', methods=['POST'])
    def api_add_entry(device_hostname):
        """
        POST Method to add defined device into the inventory.
        IP address should be provided in POST request body in JSON:
        {"ip":"x.x.x.x"}
        """
        if request.method == 'POST':
            content_type = request.headers.get('Content-Type')
            if content_type == 'application/json':
                json = request.get_json()
            else:
                return "Content-Type is not supported!"
            try:
                device = Device(**DeviceJuniper.dev_output_to_dict(json['ip']))
            except jnpr_ConnectError as err:
                print("Cannot connect to device: {0}".format(err))
                return jsonify({'error': 'Cannot connect to device'}), 404
            if Device.find_by_hostname(device_hostname):
                """Avoiding duplicate devices in the database"""
                print("{} device is present in DB".format(device.hostname))
                return jsonify({'error': 'Device is present in DB'}), 404
            db.session.add(device)
            db.session.commit()
            return jsonify({'status': 'DB was populated for {}'.
                           format(device_hostname)}), 200

    return app

if __name__ == '__main__':
    """
    Running the Flask Web app. 
    host='0.0.0.0' is required to run the Web service on all host ports
    and be available outside.
    SQLAlchemy DB and FLASK configs are defined in 'config.py'
     """
    from db import db #importing SQLAlchemy DB
    app = create_app()
    app.run(port=3000, host='0.0.0.0')