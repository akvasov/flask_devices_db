import re
import os

from db import db
from jnpr.junos import Device as JunDevice


class Device(db.Model):
    __tablename__ = 'devices' #table we use in specifed in config.py DB
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False, unique=True) #unique = True
    ip = db.Column(db.String(100), nullable=False, unique=True) #unique = True
    chassis = db.Column(db.String(100), nullable=False)
    serialnum = db.Column(db.String(100), nullable=False, unique=True)
    version = db.Column(db.String(100), nullable=True)
    type = db.Column(db.String(100), nullable=True)
    vendor = db.Column(db.String(100), nullable=False)

    @classmethod
    def find_by_hostname(cls, hostname):
        return cls.query.filter_by(hostname=hostname).first()

    def to_json(self):
        """
        Return the JSON serializable format
        """
        return {
            'id': self.id,
            'hostname': self.hostname,
            'ip': self.ip,
            'chassis': self.chassis,
            'serialnum': self.serialnum,
            'version': self.version,
            'type': self.type,
            'vendor': self.vendor
        }

class DeviceJuniper(Device):
    @staticmethod
    def dev_type(hostname):
        if re.match(r"^(\w+)j[4|9|2|8|f][1-5]$", hostname, flags=re.IGNORECASE):
            type = 'MPLS PE'
        if re.match(r"^(\w+)jn[1-5]$", hostname, flags=re.IGNORECASE):
            type = 'MPLS PE/BGP RR'
        elif re.match(r"^(\w+)j[p|l][1-5]$", hostname, flags=re.IGNORECASE):
            type = 'MPLS P'
        elif re.match(r"^(\w+)j[k|b][1-5]$", hostname, flags=re.IGNORECASE):
            type = 'Agg SW'
        elif re.match(r"^(\w+)j[i|m|3|t|x][1-5]$", hostname, flags=re.IGNORECASE):
            type = 'Mngmt SW'
        elif re.match(r"^(\w+)js[1-5]$", hostname, flags=re.IGNORECASE):
            type = 'Mngmt FW'
        return type

    @classmethod
    def dev_output_to_dict(cls, ip, username=os.environ.get('USER'), password=os.environ.get('J_PASSWD')):
        dev = JunDevice(host=ip, username=username, password=password, timeout=3, port=22)
        dev.open()
        dev_output_dict = {'hostname': dev.facts['hostname'], 'ip': ip, 'chassis': dev.facts['model'],
                           'serialnum': dev.facts['serialnumber'], 'version': dev.facts['version'],
                           'type': cls.dev_type(hostname=dev.facts['hostname']), 'vendor': 'Juniper Networks'}
        dev.close()
        return dev_output_dict