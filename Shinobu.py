import discord
from resources import *
from importlib import reload
from math import floor
from random import random
import types
import sys
import os
import socket

sys.path.append("./modules")
print("./modules")

def author_is_owner(message):
    return message.author.id == owner_id

def load_config(self):
    print("####  Loading Config  ####")
    import json
    infile = open('shinobu_config.json', 'r')
    config = json.load(infile)
    self.old_modules = self.loaded_modules
    self.loaded_modules = []
    print("Attempting to load [{0}] modules".format(len(config["modules"])))
    for module in config["modules"]:
        mod = __import__(module)
        mod = reload(mod)
        mod.accept_shinobu_instance(self)
        print("Loaded {0}, Version {1}".format(mod.__name__, mod.version))
        self.loaded_modules.append(mod)
    print("##########################\n")
    return len(self.loaded_modules)

def load_safemode_mods(shinobu, modules:list):
    loaded_modules = []
    for modname in modules:
        mod = __import__(modname)
        mod.accept_shinobu_instance(shinobu)
        loaded_modules.append(mod)
    return loaded_modules

def load_module(self, module_name):
    try:
        mod = __import__(module_name)
        mod = reload(mod)
        mod.accept_shinobu_instance(self)
        print("Loading module {0}".format(mod.__name__))
        if mod in self.loaded_modules:
            index = self.loaded_modules.index(mod)
            self.loaded_modules.remove(mod)

        self.loaded_modules.append(mod)
        return True
    except ImportError as e:
        print(str(e))
        return False

def unload_module(self, module_name):
    for module in self.loaded_modules:
        if module.__name__ == module_name:
            self.loaded_modules.remove(module)
            return True
    return False




owner_id = "142860170261692416"
shinobu = discord.Client()
shinobu.owner = owner_id
safemode_modules = load_safemode_mods(shinobu, ["ShinobuCommands", "MessageLog"])
shinobu.load_config = types.MethodType(load_config, shinobu)
shinobu.load_mod = types.MethodType(load_module, shinobu)
shinobu.unload_mod = types.MethodType(unload_module, shinobu)
shinobu.loaded_modules = []
shinobu.load_config()
shinobu.idle = False
module_description = []







@shinobu.event
async def on_ready():
    print('Logged in as:', shinobu.user.name)
    print('-------------------------')
    # print(loaded_modules)


@shinobu.event
async def on_message(message:discord.Message):

        if message.author.id == shinobu.user.id: return;

        if message.content[0] == "!" and author_is_owner(message):
            if message.content.rsplit(" ")[0] == "!safemode":
                await shinobu.send_message(message.channel, "Loading safemode modules")
                shinobu.loaded_modules = safemode_modules
            elif message.content.rsplit(" ")[0] == "!pause":
                if shinobu.idle:
                    shinobu.idle = False
                    await shinobu.send_message(message.channel, "ShinobuBot on {0} checking in".format(socket.gethostname()))
                else:
                    shinobu.idle = True
                    await shinobu.send_message(message.channel, "Paused")

        if shinobu.idle == True: return
        for module in shinobu.loaded_modules:
            try:
                await module.accept_message(message)
            except Exception as e:
                print("error",module)
                await shinobu.send_message(message.channel, "There seems to be a problem with the {0} module".format(module.__name__))
                await shinobu.send_message(message.channel,("[{0}]: " + str(e)).format(module.__name__))
                print(sys.exc_info()[0])
                print(sys.exc_traceback)

shinobu.run('MjI3NzEwMjQ2MzM0NzU4OTEz.CsKHOA.-VMTRbjonKthatdxSldkcByan8M')