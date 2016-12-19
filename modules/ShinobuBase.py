from Shinobu.client import Shinobu
from Shinobu.annotations import *
import discord
import glob
import asyncio
import os.path
from Shinobu.utility import FuzzyMatch
import collections

async def accept_message(message:discord.Message):
    if message.content == "!pause":
        shinobu.idle = True
        await shinobu.send_message(message.channel, "Paused")
    elif message.content == "!resume":
        shinobu.idle = False
        await shinobu.send_message(message.channel, "Resumed")
    if shinobu.idle:
        shinobu.stop_propagation(__name__)


def register_commands(ShinobuCommand):
    @ShinobuCommand
    @permissions("@everyone")
    @blacklist("shitpost-central")
    @description("Lists all installed commands.")
    async def commands(message: discord.Message, arguments: str):
        sent = []
        mcontent = ""
        module = arguments.rsplit(" ")[0]
        if module == "":
            output = "__Use .commands {module name} to see commands for a specific module__\n"
            await shinobu.send_message(message.channel, output)
            await shinobu.send_message(message.channel, "!modules")
            # for module in shinobu.command_descriptions:
            #     output += ("{0}\n".format(module))
        else:
            title = "__Commands in {}__\nDo .help [command] to for more info.\n".format(module)
            output = ""
            for command in sorted(shinobu.commands):
                if shinobu.commands[command].__module__ == module:
                    output += "**{}**\n".format(command)
            if output == "":
                await shinobu.send_message(message.channel, "This module contains no commands.")
            else:
                await shinobu.send_message(message.channel, title + output)

    @ShinobuCommand
    @description("Provides info on Modules and Commands")
    async def help(message: discord.Message, arguments: str):
        if arguments == "":
            await shinobu.send_message(message.channel, "!modules")
            return
        try:
            command = FuzzyMatch([x for x in shinobu.commands]).find(arguments)
            if len(command) == 0:
                module = FuzzyMatch([x.__name__ for x in shinobu.loaded_modules]).find(arguments)[0]
        except Exception as e:
            print(e)
            await shinobu.send_message(message.channel, "Could not find a command or module with that name")
            return
        additional = None
        if command:
            item = shinobu.commands[command[0]]
            type = "Command"
            name = command[0]
        elif module:
            print(module)
            item = [x for x in shinobu.loaded_modules if x.__name__ == module][0]
            type = item.type if hasattr(item, "type") else "Unknown"
            name = module
            additional = "!commands {}".format(module)
        output = "Name: **{}**\nType: **{}**\n".format(name, type)
        for attribute in ("Permissions", "Whitelist", "Blacklist", "Description", "Usage"):
            if hasattr(item, attribute):
                if isinstance(item.__getattribute__(attribute), list) or isinstance(item.__getattribute__(attribute), tuple):
                    values = ", ".join(item.__getattribute__(attribute))
                else:
                    values = item.__getattribute__(attribute)
                output += "{}: **{}**\n".format(attribute, values)
        await shinobu.send_message(message.channel, output)
        if additional:
            await shinobu.send_message(message.channel, additional)


    @ShinobuCommand
    @description("Lists loaded and unloaded modules")
    async def modules(message: discord.Message, arguments: str):
        output = ""
        if arguments == "available":
            output = "`Available Modules`\n"
            import os
            module_pool = glob.glob(os.path.dirname(__file__) + "/*")
            for module in module_pool:
                if ".py" in module:
                    module = os.path.basename(module)[:-3]
                    output += ("**{0}**\n".format(module))
                else:
                    continue
        else:
            output = "`Loaded Modules`\n"
            for module in shinobu.get_modules():
                output += ("**{0}** - Version {1}\n".format(module.__name__, module.version))
        await shinobu.send_message(message.channel, output + "\nEnter .help [module] for more info.")

    @ShinobuCommand
    @description("Reloads Shinbou from configuration")
    @permissions("Shinobu Owner")
    async def reload(message: discord.Message, arguments: str):
        start = await shinobu.send_message(message.channel, "Reloading config")
        # print("Modules loaded: ", shinobu.loaded_modules)
        mods = shinobu.load_all()
        await shinobu.edit_message(start, "Loaded {0} modules".format(mods))

    @ShinobuCommand
    @permissions("Shinobu Owner")
    async def load(message: discord.Message, arguments: str):

        if not shinobu.author_is_owner(message):
            await shinobu.send_message(message.channel, ">tries to load mod\n>isn't owner")
            return
        text = ""
        if arguments == "*":
            module_pool = glob.glob(os.path.dirname(__file__) + "/*")
            for module in module_pool:
                if ".py" in module:
                    load = True
                    module = os.path.basename(module)[:-3]
                    for mod in shinobu.loaded_modules:
                        if mod.__name__ == module:
                            load = False
                            break
                    if load and shinobu.reload_module(module):
                        text += "Loaded module {0}\n".format(module)
                    elif load:
                        text += "Failed loading module {0}\n".format(module)
            await shinobu.send_message(message.channel, text)
        else:
            for mod in get_available_modules():
                module = os.path.basename(mod)
                if ".py" in module:
                    module = module[:-3]
                if arguments.lower() in module.lower():
                    start = await shinobu.send_message(message.channel, "Loading module {0}".format(module))
                    if shinobu.reload_module(module):
                        if module not in shinobu.config["modules"]:
                            shinobu.config["modules"].append(module)
                            shinobu.write_config()
                        text = "Loaded module {0}".format(module)
                    else:
                        text = "Failed loading module {0}".format(module)
                    await shinobu.edit_message(start, text)

    @ShinobuCommand
    @permissions("Shinobu Owner")
    async def unload(message: discord.Message, arguments: str):

        if not shinobu.author_is_owner(message):
            await shinobu.send_message(message.channel, ">tries to unload mod\n>isn't owner")
            return
        start = await shinobu.send_message(message.channel, "Unloading module {0}".format(arguments))
        if shinobu.unload_module(arguments):
            shinobu.config["modules"].remove(arguments)
            shinobu.write_config()
            text = "Unloaded module {0}"
        else:
            text = "Failed unloading module {0}"
        await shinobu.edit_message(start, text.format(arguments))

    @ShinobuCommand
    @permissions("Shinobu Owner")
    async def fetch(message: discord.Message, arguments: str):
        if not shinobu.author_is_owner(message):
            await shinobu.send_message(message.channel, ">tries to fetch\n>isn't owner\n>TFW no face")
            return
        from subprocess import check_output
        out = check_output(["git", "pull"]).decode("utf-8")
        await shinobu.send_message(message.channel, out)

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

def get_available_modules():
    return glob.glob(os.path.dirname(__file__) + "/*")

version = "1.0.1"
Description = "Basic commands for Shinobu."
type="Module"
shinobu = None #type: Shinobu
