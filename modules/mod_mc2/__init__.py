from mod_mc2.rcon import RemoteConsole
from Shinobu.client import Shinobu
import discord
import json

def accept_shinobu_instance(instance):
    global shinobu, rcon
    shinobu = instance
    rcon = RemoteConsole("isogen.net", 3333, "lotsofdongers")

shinobu = None # type: Shinobu
rcon = None # type: RemoteConsole
version = "1.0.0"

def cleanup():
    if hasattr(rcon, "disconnect"):
        rcon.disconnect()

def create_tellraw(text, who="@a", color="white"):
    base = {"text":text, "color":color}
    return "/tellraw {} {}".format(who, json.dumps(base))

def shinobu_say(text, who="@a"):
    base = {"text": "[Shinobu] " + text, "color": "green"}
    return "/tellraw {} {}".format(who, json.dumps(base))

def register_commands(ShinobuCommand):
    @ShinobuCommand("Rolls n dice. By default, five.")
    async def test2(message: discord.Message, arguments: str):
        print(rcon.send("{}\n".format(arguments)))