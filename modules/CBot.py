import discord
from cleverbot import Cleverbot
async def accept_message(message:discord.Message):
    if message.content[0] == "<":
        print(message.content)
        print(message.mentions)
        if shinobu.user in message.mentions:
            phrase = message.content[len("<@227710246334758913>")+1:]
            await shinobu.send_message(message.channel,cbot.ask(phrase))


def accept_shinobu_instance(i: discord.Client):
    global shinobu
    shinobu = i

version = "1.0.0"
shinobu = None
cbot = Cleverbot()
