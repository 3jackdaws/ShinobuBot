from mod_mc2.rcon import RemoteConsole
from Shinobu.client import Shinobu
import discord
import json
import asyncio
from subprocess import call

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
    @ShinobuCommand("Rolls n dice. By default, five.", permissions=("Minecraft Operator", "Shinobu Owner"))
    async def mc_cmd(message: discord.Message, arguments: str):
        print(rcon.send("{}\n".format(arguments)))

    @ShinobuCommand("Rolls n dice. By default, five.", permissions=("Minecraft Operator", "Shinobu Owner"))
    async def restart(message: discord.Message, arguments: str):
        rcon.send("/stop\n")
        await asyncio.sleep(10)
        call(["sh", "/home/shinobu/allthemods/start.sh"])
