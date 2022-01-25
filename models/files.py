"""
This module contains files models definitions
to interact with text files
"""
import os

class FileParcer():
    """Class to define method to parse text files for this project"""

    @staticmethod
    def parse_device_file(filename=os.environ.get('DEVICES_FILE')):
        """
        Method to parse a text file defined and return a list of IP addresses in it
        Text file content example:
        192.168.1.1	device1
        192.168.1.2	device2
        192.168.1.3	device3

        Return: ['192.168.1.1','192.168.1.2','192.168.1.3']

        This method is required to connect to devices using their IP and not hostname,
        since hostnames could not be resolved over DNS.
        """
        with open(filename, 'r') as data_file:
            strings_list = data_file.read().splitlines()
            ip_list = []
            for line in strings_list:
                if line:
                    ip_list.append(str(line.split()[0]))
            return ip_list