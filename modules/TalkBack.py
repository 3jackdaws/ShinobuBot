import discord
from urllib.request import urlopen, Request
import re
import json
from classes.Shinobu import Shinobu
from textblob import TextBlob

def get_response(phrase):
    params = json.dumps({"text": phrase}).encode('utf8')
    req = Request("http://isogen.net:5001", data=params, headers={'content-type': 'application/json'})
    return json.loads(urlopen(req).read().decode("utf-8"))["response"]

def compute_certainty(message:discord.Message):
    global last_was_question, proximity, proximity
    # blob = TextBlob(message.content)
    # for word in blob.words:
    #     print(word)
    certainty = 6 - proximity
    if "shinobu" in message.content.lower() or shinobu.user in message.mentions:
        certainty = 10
    if last_was_question:
        certainty += 5
    if "?" in message.content:
        certainty += 3
    if "you" in message.content:
        certainty += 3
    if certainty > 8:
        proximity = 0
    return certainty

def compute_e_state(message:discord.Message):
    sentiment = 0
    blob = TextBlob(message.content)
    for sentence in blob.sentences:
        sentiment += sentence.sentiment.polarity
    return sentiment

def emoji_from_estate(estate):
    global propagate
    if estate < -0.65:
        propagate = False
        return "\n:rage:"
    if estate < -0.3:
        return "\n:angry:"
    elif estate < 0:
        return "\n:slight_frown:"
    else:
        return ""


def register_commands(ShinobuCommand):
    @ShinobuCommand("Set talkback certainty threshold")
    async def settb(message: discord.Message, arguments: str):
        global certainty_threshold
        try:
            certainty_threshold = int(arguments)
            shinobu.config['talkback']['certainty'] = certainty_threshold
            shinobu.write_config()
        except:
            pass

    @ShinobuCommand("Set talkback certainty threshold")
    async def debug(message: discord.Message, arguments: str):
        global debug
        if debug:
            debug = False
            await shinobu.send_message(message.channel, "Debug is now OFF")
        else:
            debug = True
            await shinobu.send_message(message.channel, "Debug is now ON")



async def accept_message(message:discord.Message):
    global last_to_me, last_was_question, e_state, proximity, propagate, debug
    certainty = compute_certainty(message)
    if certainty >= certainty_threshold:
        await shinobu.send_typing(message.channel)
        phrase = re.sub("<@227710246334758913>", "you", message.content.lower())
        # print(phrase)
        response = get_response(phrase)
        print("Shinobu: ",response)
        last_was_question = "?" in response
        e_state += compute_e_state(message)
        if e_state > 1:
            e_state = 1;
        # emoji = emoji_from_estate(e_state)
        await shinobu.send_message(message.channel, response)
        if debug: await shinobu.send_message(message.channel, "E-Val: {}\nProximity: {}\nCertainty: {}".format(e_state, proximity, certainty))
        if not propagate: shinobu.stop_propagation()
    else:
        last_to_me = False
        last_was_question = False
        print(certainty)
    proximity += 1


def accept_shinobu_instance(i: Shinobu):
    global shinobu, certainty_threshold
    shinobu = i
    try:
        certainty_threshold = shinobu.config['talkback']['certainty']
    except:
        shinobu.config['talkback'] = {"certainty":5}
        shinobu.write_config()


certainty_threshold = 0
proximity = 100
time_proximity = 0
e_state = 0
last_was_question = False
propagate = True
emotion_memory = {}
debug = False
version = "1.2.6"
shinobu = None  # type: Shinobu

