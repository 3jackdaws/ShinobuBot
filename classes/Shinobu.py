
import discord
from importlib import reload as reloadmod
from math import floor
from random import random
from glob import glob
import types
import sys
import os
import socket
import asyncio
import json

class Shinobu(discord.Client):
    def __init__(self, config_directory:str):
        super(Shinobu,self).__init__()
        self.command_list = {}
        self.command_descriptions = {}
        self.idle = False
        self.loop = asyncio.get_event_loop()
        self.config_directory = config_directory
        self.loaded_modules = []
        self.config = {}

        sys.path.append("./modules")

    def reload_module(self, module_name:str):
        for mod in self.loaded_modules:
            if mod.__name__ == module_name:
                if hasattr(mod, "cleanup"):
                    mod.cleanup()
                self.loaded_modules.remove(mod)
                if module_name in self.command_descriptions:
                    self.command_descriptions[module_name] = {}
                break
        try:
            mod = __import__(module_name)
            mod = reloadmod(mod)
            print("{0}, Version {1}".format(mod.__name__, mod.version))
            mod.accept_shinobu_instance(self)
            if hasattr(mod, "register_commands"):
                mod.register_commands(self.Command)
            self.loaded_modules.append(mod)
            return True
        except ImportError as e:
            print(str(e))
            return False

    def Command(self, description:str):
        def register_command(command_function):
            self.command_list[command_function.__name__] = command_function
            if not command_function.__module__ in self.command_descriptions:
                self.command_descriptions[command_function.__module__] = {}
            self.command_descriptions[command_function.__module__][command_function.__name__] = description
            return command_function
        return register_command

    def load_safemode_mods(self):
        self.loaded_modules = []
        self.command_descriptions = {}
        self.command_list = {}
        for modname in self.config["safemode"]:
            self.reload_module(modname)
        return len(self.loaded_modules)

    def load_all(self):
        print("####  Loading Config  ####")
        self.reload_config()
        print("Attempting to load [{0}] modules".format(len(self.config["modules"])))
        self.command_list = {}
        self.command_descriptions = {}
        for module in self.loaded_modules:
            self.unload_module(module.__name__)
        self.loaded_modules = []
        for module in self.config["modules"]:
            self.reload_module(module)
        print("##########################\n")
        return len(self.loaded_modules)

    def reload_config(self):
        infile = open(self.config_directory + 'shinobu_config.json', 'r')
        try:
            self.config = json.load(infile)
        except json.JSONDecodeError:
            infile = open(self.config_directory + 'shinobu_config.json', 'w')
            self.config = {
                "modules": ["ShinobuBase", "MessageLog", "ShinobuCommands", "TicTacToe", "RegexResponse", "TalkBack",
                            "ReminderScheduler", "AudioPlayer"],
                "safemode": ["ShinobuBase", "MessageLog"],
                "owner": "142860170261692416",
                "instance name": "Default Shinobu Instance"
            }
            json.dump(self.config, infile, indent=2)

    def author_is_owner(self, message):
        return message.author.id == self.config["owner"]

    def write_config(self):
        infile = open(self.config_directory + 'shinobu_config.json', 'w')
        json.dump(self.config, infile, indent=2)

    def unload_module(self, module_name):
        for module in self.loaded_modules:
            if module.__name__ == module_name:
                if hasattr(module, "cleanup"):
                    module.cleanup()
                self.loaded_modules.remove(module)
                if  module_name in self.command_descriptions:
                    self.command_descriptions[module_name] = {}
                return True
        return False

    def quick_send(self, channel:discord.Channel, message):
        print("Quick sending: [{0}] {1}".format(channel.name, message))
        asyncio.ensure_future(self.send_message(channel, message), loop=self.loop)