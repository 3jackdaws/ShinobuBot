from random import random
from math import floor
import discord
shinobu_exit = "http://i.imgur.com/FR3I1dH.gif"
shinobu_eat_donut = ["http://i.imgur.com/DL5qmtL.gif",
                     "http://i.imgur.com/16GrVjp.gif"]
shinobu_sit = "http://67.media.tumblr.com/7262e5ad2eff4e1f571d633356d1f405/tumblr_ntrmls3Vmk1tcyz0do2_500.jpg"

shinobu_greeting = ["Hi, ",
                    "Hello, "]

shinobu_pat = [""]

def read_config():
    import json
    infile = open('shinobu_config.json', 'r')
    jsonstring = infile.read()
    return json.loads(jsonstring)

def load_config():
    modules_to_load = []
    for module in read_config().modules:
        modules_to_load.append(module)
    map(__import__, modules_to_load)

def choose_random(resource_list:list):
    return resource_list[floor(len(resource_list)*random())]

def overwatch_hero(channel: discord.Message.channel,hero:str):
    pass

def write_pr():
    import json
    with open('pair_response.json', 'w') as outfile:
        json.dump(pair_response, outfile, ensure_ascii=False)

def read_pr():
    import json
    infile = open('pair_response.json', 'r')
    jsonstring = infile.read()
    return json.loads(jsonstring)

pair_response = read_pr()