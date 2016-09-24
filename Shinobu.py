import discord
from resources import *
from importlib import reload
from math import floor
from random import random
import types

def author_is_owner(message):
    return message.author.id == owner_id

def load_config(self):
    import json
    infile = open('shinobu_config.json', 'r')
    config = json.load(infile)
    old_modules = self.loaded_modules
    self.loaded_modules = []
    for module in config["modules"]:
        mod = __import__(module)
        mod = reload(mod)
        mod.accept_shinobu_instance(self)
        print(module, mod.version)
        self.loaded_modules.append(mod)
    return len(self.loaded_modules)







owner_id = "142860170261692416"
shinobu = discord.Client()
shinobu.owner = owner_id
shinobu.load_config = types.MethodType(load_config, shinobu)
shinobu.loaded_modules = []
shinobu.load_config()
module_description = []







@shinobu.event
async def on_ready():
    print('Logged in as:', shinobu.user.name)
    print('-------------------------')
    # print(loaded_modules)


@shinobu.event
async def on_message(message:discord.Message):

        print("[" + message.author.name +"]", "\n" + message.content)
        if message.author.id == shinobu.user.id: return;

        for module in shinobu.loaded_modules:
            try:
                await module.accept_message(message)
            except Exception as e:
                print("error",module)
                await shinobu.send_message(message.channel, "There seems to be a problem with the {0} module".format(module.__name__))
                print(("[{0}]: " + str(e)).format(module.__name__))


shinobu.run('MjI3NzEwMjQ2MzM0NzU4OTEz.CsKHOA.-VMTRbjonKthatdxSldkcByan8M')