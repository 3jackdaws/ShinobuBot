from classes.Shinobu import Shinobu
import discord
import glob
import asyncio

async def accept_message(message:discord.Message):
    pass

def register_commands(ShinobuCommand):
    @ShinobuCommand("Lists all of the available commands")
    async def commands(message: discord.Message, arguments: str):
        sent = []
        mcontent = ""
        module = arguments.rsplit(" ")[0]
        if module == "":
            output = "__Use .commands {module name} to see commands for a specific module__\n"
            for module in shinobu.command_descriptions:
                output += ("{0}\n".format(module))
        else:
            output = "__{}__\n".format(module)
            for command in shinobu.command_descriptions[module]:
                output += "**{}** - {}\n".format(command, shinobu.command_descriptions[module][command])
        await shinobu.send_message(message.channel, output)




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

    @ShinobuCommand("Tells Shinobu to reload her configuration")
    async def reload(message: discord.Message, arguments: str):
        if not shinobu.author_is_owner(message):
            await shinobu.send_message(message.channel, ">tries to reload config\n>isn't owner\n>mfw no face")
            return
        start = await shinobu.send_message(message.channel, "Reloading config")
        mods = shinobu.load_all()
        await shinobu.edit_message(start, "Loaded {0} modules".format(mods))

    @ShinobuCommand("Tells Shinobu to load or reload a specified module")
    async def load(message: discord.Message, arguments: str):

        if not shinobu.author_is_owner(message):
            await shinobu.send_message(message.channel, ">tries to load mod\n>isn't owner")
            return
        text = ""
        if arguments == "*":
            import os
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
            start = await shinobu.send_message(message.channel, "Loading module {0}".format(arguments))
            if shinobu.reload_module(arguments):
                text = "Loaded module {0}".format(arguments)
            else:
                text = "Failed loading module {0}".format(arguments)
            await shinobu.edit_message(start, text)

    @ShinobuCommand("Tells Shinobu to load or reload a specified module")
    async def unload(message: discord.Message, arguments: str):

        if not shinobu.author_is_owner(message):
            await shinobu.send_message(message.channel, ">tries to unload mod\n>isn't owner")
            return
        start = await shinobu.send_message(message.channel, "Unloading module {0}".format(arguments))
        if shinobu.unload_module(arguments):
            text = "Unloaded module {0}"
        else:
            text = "Failed unloading module {0}"
        await shinobu.edit_message(start, text.format(arguments))

    @ShinobuCommand("Pulls latest from the ShinobuBot repo")
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
