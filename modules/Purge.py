from classes.Shinobu import Shinobu
import discord
import re
async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance # type: Shinobu




version = "0.0.3"
shinobu = None # type: Shinobu

def register_commands(ShinobuCommand):
    @ShinobuCommand("purges all")
    async def purge(message:discord.Message, arguments:str):
        if shinobu.author_is_owner(message):
            channel = message.channel
            limit = int(arguments)
            await shinobu.purge_from(channel, limit=limit)