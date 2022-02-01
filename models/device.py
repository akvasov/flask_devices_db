"""
This module contains network devices' model definitions
to connect and gather inventory of the device over NetConf,
store this inventory data into POSTGRESQL DB by leveraging Flask-SQLAlchemy
"""

import re
import os
import asyncio

from jnpr.junos.exception import ConnectError, ProbeError, ConfigLoadError
from jnpr.junos import Device as JunDevice

from db import db


class Device(db.Model):
    """Flask-SQLAlchemy DB definition to store devices inventory"""
    __tablename__ = 'devices'  # table we use in specifed in config.py POSTGRESQL DB
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False, unique=True)
    ip = db.Column(db.String(100), nullable=False, unique=True)
    chassis = db.Column(db.String(100), nullable=False)
    serialnum = db.Column(db.String(100), nullable=False, unique=True)
    version = db.Column(db.String(100), nullable=True)
    type = db.Column(db.String(100), nullable=True)
    vendor = db.Column(db.String(100), nullable=False)

    @classmethod
    def find_by_hostname(cls, hostname):
        """A query to find if a device is present into DB"""
        return cls.query.filter_by(hostname=hostname).first()

    def to_json(self):
        """Return the JSON serializable format"""
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
    """Child class of Device for methods relevant to Juniper devices"""

    @staticmethod
    def dev_type(hostname):
        """Return the device type according to the hostname format"""
        if re.match(r"^wrcsmalbj[4|8|f|n|l|p|k|s|i|m|3|t|x][1-9]$",
                    hostname, flags=re.I):
            return 'LAB device'
        if re.match(r"^(\w+)j[4|9|2|8|f][1-9]$", hostname, flags=re.I):
            devtype = 'MPLS PE'
        if re.match(r"^(\w+)jn[1-9]$", hostname, flags=re.I):
            devtype = 'MPLS PE/BGP RR'
        elif re.match(r"^(\w+)j[p|l][1-9]$", hostname, flags=re.I):
            devtype = 'MPLS P'
        elif re.match(r"^(\w+)j[k|b][1-9]$", hostname, flags=re.I):
            devtype = 'Agg SW'
        elif re.match(r"^(\w+)j[i|m|3|t|x][1-9]$", hostname, flags=re.I):
            devtype = 'Mngmt SW'
        elif re.match(r"^(\w+)js[1-9]$", hostname, flags=re.I):
            devtype = 'Mngmt FW'
        else:
            devtype = 'N/A'
        return devtype


    @classmethod
    def dev_output_to_dict(cls, ip, username=os.environ.get('USER'),
                           password=os.environ.get('J_PASSWD')):
        """
        Connect to a device IP over NEtConf and return the inventory data in a
        dictionary format
        """
        dev = JunDevice(host=ip,
                        username=username,
                        password=password,
                        timeout=3,
                        port=22)
        dev.open(auto_probe=5)
        dev_output_dict = {
                           'hostname': dev.facts['hostname'],
                           'ip': ip,
                           'chassis': dev.facts['model'],
                           'serialnum': dev.facts['serialnumber'],
                           'version': dev.facts['version'],
                           'type': cls.dev_type(dev.facts['hostname']),
                           'vendor': 'Juniper Networks'
        }
        dev.close()
        return dev_output_dict
