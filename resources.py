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


    # {"even lift":["fite me irl, i swear on me mum i'll hook ya right in the gobber"],
    #              "even drift":["wew lad"],
    #              "re+":["wew lad, careful with that autism"],
    #              "kek":["lel"],
    #              "lol":["kek"],
    #              "overwatch":[
    #                  "Overwatch is the best, my favorite hero is Widowmaker.  What's an objective?",
    #                  "Ya bb. Bastion is the best hero.  Fuck u Mercy why u not healing >:((("
    #              ],
    #              "h(ello|i|ey|iya)":["sup :)", "hey =)", "how's it going", "hi :3", "hi :)", "hello friendo :^)"]
    #              }
pair_response = read_pr()