from Shinobu.client import Shinobu
import discord
import glob
import asyncio
import os.path
from Shinobu.utility import FuzzyMatch

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
    @ShinobuCommand("Lists all of the available commands", permissions=('@everyone'))
    async def commands(message: discord.Message, arguments: str):
        sent = []
        mcontent = ""
        module = arguments.rsplit(" ")[0]
        if module == "":
            output = "__Use .commands {module name} to see commands for a specific module__\n"
            await shinobu.send_message(message.channel, output)
            await shinobu.send_message(message.channel, "!modules rm")
            # for module in shinobu.command_descriptions:
            #     output += ("{0}\n".format(module))
        else:
            title = "__{}__\n".format(module)
            output = ""
            for command in sorted(shinobu.command_list, key=lambda x:x["command"]):
                if command['module'] == module:
                    output += "**{}** - {}\n".format(command['command'], command['description'])
            if output == "":
                output = "Module not loaded."
            await shinobu.send_message(message.channel, title + output)

    @ShinobuCommand("Lists all of the available commands")
    async def info(message: discord.Message, arguments: str):
        try:
            module_name = FuzzyMatch([x['command'] for x in shinobu.command_list]).find(arguments)[0]
        except:
            await shinobu.send_message(message.channel, "Could not find a command with that name")
            return
        command = [x for x in shinobu.command_list if x['command'] == module_name][0]
        output = "Command: **" + command['command'] + "**\n"
        output += "Description: {}\n".format(command['description'])
        output += "Module: **" + command['module'] + "**\n"
        output += "Permissions: **{}**\n".format(command['permissions'] if "permissions" in command else "everyone")
        output += "Disallowed in: **{}**\n".format(command['blacklist'] if "blacklist" in command else "None")
        output += "Allowed in: **" + (command['whitelist'] + "**.") if "whitelist" in command else ""
        await shinobu.send_message(message.channel, output)


    @ShinobuCommand("Alias for .commands")
    async def help(message: discord.Message, arguments: str):
        await shinobu.send_message(message.channel, "!commands")

    @ShinobuCommand("Lists all loaded modules")
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
            for module in shinobu.loaded_modules:
                output += ("**{0}** - Version {1}\n".format(module.__name__, module.version))
        await shinobu.send_message(message.channel, output)

    @ShinobuCommand("Tells Shinobu to reload her configuration", permissions = ("Shinobu Owner"), whitelist=("bot-shitposting", "the-holodeck"))
    async def reload(message: discord.Message, arguments: str):
        start = await shinobu.send_message(message.channel, "Reloading config")
        # print("Modules loaded: ", shinobu.loaded_modules)
        mods = shinobu.load_all()
        await shinobu.edit_message(start, "Loaded {0} modules".format(mods))

    @ShinobuCommand("Tells Shinobu to load or reload a specified module", permissions = ("Shinobu Owner"), whitelist=("bot-shitposting", "the-holodeck"))
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

    @ShinobuCommand("Tells Shinobu to load or reload a specified module", permissions = ("Shinobu Owner"), whitelist=("bot-shitposting"))
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

    @ShinobuCommand("Pulls latest from the ShinobuBot repo", permissions = ("Shinobu Owner"), whitelist=("bot-shitposting"))
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

version = "1.0.1"
shinobu = None #type: Shinobu

def get_available_modules():
    return glob.glob(os.path.dirname(__file__) + "/*")
