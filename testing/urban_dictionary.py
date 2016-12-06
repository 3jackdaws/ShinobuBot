from urllib.request import urlopen,Request
from urllib.parse import urlencode
import re
import json

def get_ud_definition(word):
    query = urlencode({"term":word})
    url_base = "http://api.urbandictionary.com/v0/define?"
    text = json.loads(urlopen(url_base + query).read().decode('utf-8'))
    return text["list"][0]['definition']



get_ud_definition("alabama hot pocket")