from .highlevel import *
from Shinobu.utility import ConfigManager
config = ConfigManager("resources/database_connector.json")
password = config['password'].value
dbopen(password)

def accept_shinobu_instance(shinobu):
    pass

type = "Connector"
Description = "Isogen database connector with Record class."
version = "1.0.2"