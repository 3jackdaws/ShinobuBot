import discord
from urllib.request import urlopen, Request
import re
import json

def get_response(phrase):
    params = params = json.dumps({"text": phrase}).encode('utf8')

    req = Request("http://127.0.0.1:5001", data=params, headers={'content-type': 'application/json'})
    return json.loads(urlopen(req).read().decode("utf-8"))["response"]

async def accept_message(message:discord.Message):
    global last_to_me, last_was_question
    if shinobu.user in message.mentions or "shinobu" in message.content.lower() or last_was_question or (last_to_me and ("you" in message.content or "?" in message.content)):
        last_to_me = True
        phrase = re.sub("<@227710246334758913>", "you", message.content.lower())
        # phrase = re.sub("shinobu", "you", message.content)
        print(phrase)
        response = get_response(phrase)
        print(response)
        if "?" in response:
            last_was_question = True
        else:
            last_was_question = False
        await shinobu.send_message(message.channel, response)
    else:
        last_to_me = False
        last_was_question = False


def accept_shinobu_instance(i: discord.Client):
    global shinobu
    shinobu = i

last_to_me = False
last_was_question = False
version = "1.2.3"
shinobu = None
