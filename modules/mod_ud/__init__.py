from urllib.request import urlopen,Request
from urllib.parse import urlencode
import json
import discord
from Shinobu.client import Shinobu
from Shinobu.annotations import *

def get_ud_definition(word):
    query = urlencode({"term":word})
    url_base = "http://api.urbandictionary.com/v0/define?"
    text = json.loads(urlopen(url_base + query).read().decode('utf-8'))
    return text["list"][0]['definition']

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

shinobu = None # type: Shinobu
version = "1.0.0"

def register_commands(ShinobuCommand):
    @ShinobuCommand
    @description("Looks up the word or phrase on urban dictionary")
    async def ud(message: discord.Message, arguments: str):
        definition = get_ud_definition(arguments)
        await shinobu.send_message(message.channel, "**{}**\n{}".format(arguments,definition))


