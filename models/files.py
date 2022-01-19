import os

class FileParcer():
    @staticmethod
    def parse_device_file(filename=os.environ.get('DEVICES_FILE')):
        with open(filename, 'r') as data_file:
            strings_list = data_file.read().splitlines()
            ip_list = []
            for line in strings_list:
                if line:
                    ip_list.append(str(line.split()[0]))
            return ip_list