import discord
from resources import *
from importlib import reload as reloadmod
from math import floor
from random import random
from glob import glob
import types
import sys
import os
import socket

sys.path.append("./modules")

ShinobuCommandList = {}
ShinobuCommandDesc = {}

def author_is_owner(self, message):
    return message.author.id == self.config["owner"]

def reload_config(self):
    import json
    infile = open('shinobu_config.json', 'r')
    self.config = json.load(infile)

def load_all(self):
    print("####  Loading Config  ####")
    self.reload_config()
    print("Attempting to load [{0}] modules".format(len(self.config["modules"])))
    for module in self.config["modules"]:
        shinobu.reload_module(module)
    print("##########################\n")
    return len(self.loaded_modules)

def load_safemode_mods(self):
    global ShinobuCommandDesc
    global ShinobuCommandList
    ShinobuCommandDesc = {}
    ShinobuCommandList = {}
    self.loaded_modules = []
    for modname in self.config["safemode"]:
        shinobu.reload_module(modname)
    shinobu.command_description = ShinobuCommandDesc
    shinobu.start_private_message()
    return len(self.loaded_modules)

def ShinobuCommand(description):
    global ShinobuCommandList
    global ShinobuCommandDesc

    def find_command(command_function):
        ShinobuCommandList[command_function.__name__] = command_function
        if not command_function.__module__ in ShinobuCommandDesc:
            ShinobuCommandDesc[command_function.__module__] = {}
        ShinobuCommandDesc[command_function.__module__][command_function.__name__] = description
        return command_function
    return find_command



def load_module(self, module_name):
    for mod in self.loaded_modules:
        if mod.__name__ == module_name:
            if hasattr(mod, "cleanup"):
                mod.cleanup()
            self.loaded_modules.remove(mod)
            break

    try:
        mod = __import__(module_name)
        mod = reloadmod(mod)
        mod.accept_shinobu_instance(self)
        if hasattr(mod, "register_commands"):
            mod.register_commands(ShinobuCommand)
        print("{0}, Version {1}".format(mod.__name__, mod.version))

        self.loaded_modules.append(mod)
        return True
    except ImportError as e:
        print(str(e))
        return False

def unload_module(self, module_name):
    for module in self.loaded_modules:
        if module.__name__ == module_name:
            if hasattr(module, "cleanup"):
                module.cleanup()
            self.loaded_modules.remove(module)
            return True
    return False



shinobu = discord.Client()

##########BIND NEW METHODS
shinobu.reload_all = types.MethodType(load_all, shinobu)
shinobu.reload_module = types.MethodType(load_module, shinobu)
shinobu.unload_module = types.MethodType(unload_module, shinobu)
shinobu.reload_config = types.MethodType(reload_config, shinobu)
shinobu.safemode = types.MethodType(load_safemode_mods, shinobu)
shinobu.author_is_owner = types.MethodType(author_is_owner, shinobu)
#############################################################

##########PRE-INITIALIZATION
shinobu.loaded_modules = []
shinobu.command_description = ShinobuCommandDesc

shinobu.reload_config()
shinobu.reload_all()
shinobu.idle = False



@shinobu.event
async def on_ready():
    print('Logged in as:', shinobu.user.name)
    print('-------------------------')
    # print(loaded_modules)


@shinobu.event
async def on_message(message:discord.Message):

        if message.author.id == shinobu.user.id: return;

        if message.content[0] == "!" and shinobu.author_is_owner(message):
            if message.content.rsplit(" ")[0] == "!safemode":
                await shinobu.send_message(message.channel, "Loading safemode modules")
                shinobu.safemode()
            elif message.content.rsplit(" ")[0] == "!pause":
                if shinobu.idle:
                    shinobu.idle = False
                    await shinobu.change_status(idle=False)
                    await shinobu.send_message(message.channel, "ShinobuBot on {0} checking in".format(socket.gethostname()))
                    print("UNPAUSED")
                else:
                    shinobu.idle = True
                    await shinobu.change_status(idle=True)
                    await shinobu.send_message(message.channel, "Paused")
                    print("PAUSED")

        if shinobu.idle == True: return
        if message.content[0] is ".":
            command = message.content.rsplit(" ")[0][1:]
            arguments = " ".join(message.content.rsplit(" ")[1:])
            if command in ShinobuCommandList:
                await ShinobuCommandList[command](message, arguments)

        else:
            for module in shinobu.loaded_modules:
                try:
                    await module.accept_message(message)
                except Exception as e:
                    await shinobu.send_message(message.channel, "There seems to be a problem with the {0} module".format(module.__name__))
                    await shinobu.send_message(message.channel,("[{0}]: " + str(e)).format(module.__name__))
                    print(sys.exc_info()[0])
                    print(sys.exc_traceback)

shinobu.run('MjI3NzEwMjQ2MzM0NzU4OTEz.CsKHOA.-VMTRbjonKthatdxSldkcByan8M')