import re
from Shinobu.database import *


db = None

def set_db_mod(module):
    global db
    db = module

def add_shitpost()