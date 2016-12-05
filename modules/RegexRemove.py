import discord
from classes.Shinobu import Shinobu

async def accept_message(message:discord.Message):
    for word in removals:
        if word in message.content:
            await shinobu.delete_message(message)

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

shinobu = None # type: discord.Client


removals = [
    "cuck",
    "cuckold"
]
