import discord
from cleverbot import Cleverbot
import re
async def accept_message(message:discord.Message):
    global last_to_me
    if shinobu.user in message.mentions or "shinobu" in message.content.lower() or (last_to_me and "you" in message.content):
        last_to_me = True
        phrase = re.sub("<@227710246334758913>", "you", message.content)
        print(phrase)
        await shinobu.send_message(message.channel,cbot.ask(phrase))
    else:
        last_to_me = False


def accept_shinobu_instance(i: discord.Client):
    global shinobu
    shinobu = i

last_to_me = False
version = "1.0.0"
shinobu = None
cbot = Cleverbot()
