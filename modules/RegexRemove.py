import discord
from classes.Shinobu import Shinobu

async def accept_message(message:discord.Message):
    for word in removals:
        if word in message.content:
            await shinobu.delete_message(message)
            shinobu.stop_propagation()

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

shinobu = None # type: Shinobu
version = "1.0.0"

removals = [
    "cuck",
    "cuckold"
]
