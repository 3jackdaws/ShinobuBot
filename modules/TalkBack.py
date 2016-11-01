import discord
from cleverbot import Cleverbot
import re
async def accept_message(message:discord.Message):
    global last_to_me, last_was_question
    if shinobu.user in message.mentions or "shinobu" in message.content.lower() or last_was_question or (last_to_me and "you" in message.content):
        last_to_me = True
        phrase = re.sub("<@227710246334758913>", "you", message.content)
        print(phrase)
        response = cbot.ask(phrase)
        if "?" in response:
            last_was_question = True
        else:
            last_was_question = False
        await shinobu.send_message(message.channel,)
    else:
        last_to_me = False
        last_was_question = False


def accept_shinobu_instance(i: discord.Client):
    global shinobu
    shinobu = i

last_to_me = False
last_was_question = False
version = "1.0.0"
shinobu = None
cbot = Cleverbot()
