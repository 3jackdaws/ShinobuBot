import discord
from random import random
import math
import re
from classes.Shinobu import Shinobu





def choose_from(choices:list):
    if len(choices) == 1:
        return choices[0]
    else:
        index = math.floor(random()*len(choices))
        return choices[index]

async def accept_message(message:discord.Message):
    if message.content[0].isalpha():
        response = get_reponse(message.content.lower())
        if response == "{{FILTER}}":
            await shinobu.delete_message(message)
        elif response is not None:
            await shinobu.send_message(message.channel, response)




def load_patterns():
    import json
    global patterned_responses
    pattern_file = open("resources/patterned_responses.json", "a+")
    pattern_file.seek(0)
    try:
        patterned_responses = json.load(pattern_file)
    except json.decoder.JSONDecodeError as err:
        patterned_responses = []
    return len(patterned_responses)

def write_patterns():
    import json
    global patterned_responses
    pattern_file = open("resources/patterned_responses.json", "w")
    json.dump(patterned_responses, pattern_file, indent=4)

def accept_shinobu_instance(i:discord.Client):
    global shinobu
    ShinobuCommand = None
    shinobu = i



def register_commands(ShinobuCommand):
#####START REGISTER COMMANDS
    @ShinobuCommand("Tells Shinobu automatically delete matched messages", ["owner"])
    async def filter(message: discord.Message, arguments: str):
        if add_response(arguments, "{{FILTER}}"):
            write_patterns()
        else:
            await shinobu.send_message(message.channel, "That type of pattern is not allowed.")

    @ShinobuCommand("Tells Shinobu to learn a paired response", ['owner'])
    async def learn(message: discord.Message, arguments: str):
        components = arguments.split("|")
        if len(components) < 2:
            await shinobu.send_message(message.channel,
                                       "What is that supposed to mean?  You have to have a component I'm looking for and a component I respond with.  Those need to be separated by a pipe symbol '|'")
        else:
            if add_response(components[0], components[1]):
                write_patterns()
            else:
                await shinobu.send_message(message.channel, "That type of pattern is not allowed.")
#####NEXT COMMAND
    @ShinobuCommand("Tells Shinobu to unlearn a paired response", ['owner'])
    async def unlearn(message: discord.Message, arguments: str):
        for pair in patterned_responses:
            if pair[0] == arguments:
                patterned_responses.remove(pair)
        write_patterns()

#####NEXT COMMAND
    @ShinobuCommand("Tells Shinobu to unlearn a paired response and never learn it again", ['owner'])
    async def block(message: discord.Message, arguments: str):
        for pair in patterned_responses:
            if pair[0] == arguments:
                pair[1] = None
        write_patterns()
#####NEXT COMMAND
    @ShinobuCommand("Looks up the pair that a specific message matches to", ['all'])
    async def relookup(message: discord.Message, arguments: str):
        for pair in patterned_responses:
            if pair[1] == None: continue
            regexp = "(^|[^a-z])" + pair[0] + "($|[^a-z])"
            if re.search(regexp, arguments):
                await shinobu.send_message(message.channel, pair.__str__())
                return
        await shinobu.send_message(message.channel, "No matches")

def test_reg(reg):
    regexp = "(^|[^a-z])" + reg + "($|[^a-z])"
    for string in ["or", "a", "to", "the", "from", "for"]:
        if re.match(regexp, string):
            return False
    return True

def add_response(regex, response, raw=False):
    global patterned_responses
    if not test_reg(regex):
        return False
    inserted = False
    for pair in patterned_responses:
        if regex == pair[0]:
            if pair[1] != None:
                pair[1].append(response)
            inserted = True
    if not inserted:
        patterned_responses.append([regex,[response]])
    return True


def get_reponse(message):
    for pair in patterned_responses:
        if pair[1] == None: continue
        regexp = "(^|[^a-z])" + pair[0] + "($|[^a-z])"
        if re.search(regexp, message):
            return choose_from(pair[1])
    return None


version = "1.0.0"
shinobu = None #type: Shinobu
patterned_responses = []
compiled_patterns = []
load_patterns()

