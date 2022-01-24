import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, url_for, jsonify, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from jnpr.junos.exception import ConnectError as jnpr_ConnectError
from sqlalchemy.orm import exc


from models.files import FileParcer
from models.login_forms import LoginForm, SignUPForm
from models.device import Device, DeviceJuniper
from models.user import User

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object("config.Config")
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @app.before_first_request
    def create_tables():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def return_to_index(status):
        return render_template('index.html', status=status)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route('/')
    def index():
        return return_to_index('')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = SignUPForm()
        act_passwd = os.environ.get('SIGNUP_PASSWD')
        if form.validate_on_submit():
            if act_passwd == form.act_passwd.data:
                hashed_password = generate_password_hash(form.password.data, method='sha256')
                db.session.add(User(username=form.username.data, password=hashed_password))
                db.session.commit()
                return return_to_index('The user has been created. Log in please!')
            else:
                return return_to_index('Error. The SIGNUP activation password is wrong')
        return render_template('signup.html', form=form)

    @app.route('/login', methods=['GET','POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            try:
                user = User.find_by_username(form.username.data)
            except exc.NoResultFound:
                return return_to_index('This user does not exist. Sign UP!')
            if user:
                if check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    return redirect(url_for('devices'))
            return return_to_index('Invalid username or password')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return return_to_index('The user has been logged out')

    @app.route('/devices')
    @login_required
    def devices():
        devices = Device.query.order_by(Device.type).all()
        return render_template('devices_index.html', devices=devices)

    @app.route('/devices/<device_hostname>')
    @login_required
    def devices_show(device_hostname):
        try:
            device = Device.find_by_hostname(device_hostname)
            return render_template('devices_show.html', device=device)
        except exc.NoResultFound:
            abort(404)

    @app.route('/api/devices')
    def api_devices_all():
        devices = Device.query.all()
        return jsonify([device.to_json() for device in devices])

    @app.route('/api/devices/<device_hostname>')
    def api_devices_show(device_hostname):
        if request.method == 'GET':
            try:
                device = Device.find_by_hostname(device_hostname)
                return jsonify(device.to_json())
            except exc.NoResultFound:
                return jsonify({'error': 'Device not found'}), 404

    @app.route('/api/populatedb/<device_filename>')
    def api_populatedb(device_filename):
        hostnames_list = []
        for ip in FileParcer.parse_device_file(device_filename):
            try:
                    device = Device(**DeviceJuniper.dev_output_to_dict(ip))
            except jnpr_ConnectError as err:
                    print("Cannot connect to device: {0}".format(err))
                    continue
            #avoiding duplicate hostnames in the database
            if Device.find_by_hostname(device.hostname):
                print("{} device is present in DB".format(device.hostname))
                continue
            hostnames_list.append(device.hostname)
            db.session.add(device)
            db.session.commit()
        return jsonify({'status': 'DB was populated for {}'.format(hostnames_list)}), 200

    @app.route('/api/delete/<device_hostname>', methods=['DELETE'])
    def api_delete_entry(device_hostname):
        device = Device.find_by_hostname(device_hostname)
        if device:
            db.session.delete(device)
            db.session.commit()
            return jsonify({'status': 'DB entry was cleared for {}'.format(device_hostname)}), 200
        else:
            return jsonify({'error': 'Device is NOT present in DB'}), 404

    @app.route('/api/add/<device_hostname>', methods=['POST'])
    def api_add_entry(device_hostname):
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
                print("{} device is present in DB".format(device.hostname))
                return jsonify({'error': 'Device is present in DB'}), 404
            db.session.add(device)
            db.session.commit()
            return jsonify({'status': 'DB was populated for {}'.format(device_hostname)}), 200

    return app

if __name__ == '__main__':
    from db import db
    app = create_app()
    app.run(port=3000, host='0.0.0.0', debug=True)