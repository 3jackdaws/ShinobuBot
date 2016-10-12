import discord
import re
async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu, operators
    shinobu = instance
    try:
        operators = shinobu.config['minecraft_operators']
    except:
        operators = []



version = "0.0.3"
shinobu = None # type: discord.Client

def register_commands(ShinobuCommand):
    @ShinobuCommand("purges all")
    async def purge(message:discord.Message, arguments:str):
        channel = message.channel
        limit = int(arguments)
        await shinobu.purge_from(channel, limit=limit)