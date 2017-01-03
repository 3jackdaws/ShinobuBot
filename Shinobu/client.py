
import discord
from importlib import reload as reloadmod
import sys
import asyncio
import json
import Shinobu.database as database

class Shinobu(discord.Client):
    def __init__(self, config_directory:str):
        super(Shinobu,self).__init__()
        self.commands = {}
        self.idle = False
        self.loop = asyncio.get_event_loop()
        self.config_directory = config_directory
        self.__modules = {}
        self.__load_order = []
        self.config = {}
        self.log = lambda *x: print(*x)
        sys.path.append("./modules")
        self.login_email = ""
        self.login_password = ""
        self.login_token = ""
        self.owner = ""
        self.instance_name = ""
        self.db = database
        self.__bootstrap()



    def permissions_manager(self, command, message:discord.Message):
        if not callable(command):
            raise Exception("First parameter of permissions manager call must be a callable object.")
        command = command.__dict__
        if "Blacklist" in command:
            if message.channel.name in command['Blacklist']:
                raise PermissionError("That command cannot be used in this channel.")

        if "Whitelist" in command:
            if message.channel.name not in command['Whitelist']:
                raise PermissionError("That command cannot be used in this channel.")

        if "Permissions" in command:
            self.log("Checking permissions")
            if message.author.id == self.owner:
                return True
            for role in message.author.roles:
                if role.name in command['Permissions']:
                    return True
            raise PermissionError("You do not have permissions to use that command.")

    def exec(self, command, message:discord.Message):
        if command in self.commands:
            com_func = self.commands[command]
            try:
                self.permissions_manager(com_func, message)
                arguments = " ".join(message.content.rsplit(" ")[1:])

                self.invoke(com_func(message, arguments))
            except PermissionError as e:
                self.log("{} attempted to execute a command with invalid permissions.".format(message.author.nick))
                self.invoke(self.send_message(message.channel, str(e)))


    def reload_module(self, module_name:str):
        try:
            if module_name in self.__modules:
                module = self.__modules[module_name]
                if hasattr(module, "stop_module"):
                    module.stop_module()
                self.__modules[module_name] = reloadmod(self.__modules[module_name])
                self.log("Reloading {}".format(module_name))
            else:
                print("Loading {}".format(module_name))
                self.__modules[module_name] = __import__(module_name)

            if hasattr(self.__modules[module_name], "accept_shinobu_instance"):
                self.__modules[module_name].accept_shinobu_instance(self)

            if hasattr(self.__modules[module_name], "register_commands"):
                self.__modules[module_name].register_commands(self.Command)
            return True
        except Exception as e:
            self.log(e)
            return False



    def Command(self, command_function):
        self.commands[command_function.__name__] = command_function
        return command_function

    def read_json(self, filename):
        file = open(filename, "r")
        return json.load(file)

    def write_json(self, filename, object):
        file = open(filename, "w+")
        json.dump(object, file, indent=4)

    def __bootstrap(self):
        try:
            self.config = self.read_json(self.config_directory + "config.json")
            self.login_email = self.config["discord"]["email"]
            self.login_password = self.config["discord"]["password"]
            self.login_token = self.config["discord"]["token"]
            self.owner = self.config["owner"]
            self.instance_name = self.config["instance_name"]
            database.dbopen(**self.config["database"])
            self.config = database.DatabaseDict("ShinobuConfig")
            if "autoload" not in self.config:
                self.config["autoload"] = [
                    "MessageLog",
                    "ShinobuBase",
                    "ShinobuCommands"
                ]
            self.config.commit()
            self.__load_order = self.config["autoload"]

        except FileNotFoundError as e:
            self.write_json(self.config_directory + "config.json", {
                "database":{
                    "host":"localhost",
                    "database":"shinobu",
                    "user":"shinobu",
                    "password":"shinobu"
                },
                "discord":{
                    "email":"",
                    "password":"",
                    "token":""
                },
                "owner":"put owner id here",
                "instance_name":"Default Instance"
            })



    def load_all(self):
        print("####  Loading Config  ####")
        print("Attempting to load [{0}] modules".format(len(self.__load_order)))
        self.commands = {}
        self.__bootstrap()
        for module in self.__load_order:
            self.reload_module(module)
        print("##########################\n")
        return len(self.__modules)


    def author_is_owner(self, message):
        return message.author.id == self.owner

    def write_config(self):
        self.config.save()

    def unload_module(self, module_name):
        if module_name in self.__modules:
            if hasattr(self.__modules[module_name], "stop_module"):
                self.__modules[module_name].stop_module()
            del self.__modules[module_name]


    def quick_send(self, channel:discord.Channel, message):
        print("Quick sending: [{0}] {1}".format(channel.name, message))
        asyncio.ensure_future(self.send_message(channel, message), loop=self.loop)

    def invoke(self, coroutine:asyncio.futures.Future):
        return asyncio.ensure_future(coroutine, loop=self.loop)

    def stop_propagation(self, name):
        raise StopPropagationException(name)

    def get_modules(self, type=None):
        if type:
            return [module for module in self.__modules.values() if module.type.lower() == type]
        else:
            return self.__modules.values()

    def get_module(self, name):
        for module in self.__modules.values():
            if module.__name__ == name:
                return module







class StopPropagationException(Exception):
    pass