import discord
import glob

async def accept_message(message:discord.Message):
    pass

def register_commands(ShinobuCommand):
    @ShinobuCommand("Lists all of the available commands")
    async def commands(message: discord.Message, arguments: str):
        ShinobuCommandDesc = shinobu.command_description
        output = "***COMMANDS***\n"
        for module in sorted(ShinobuCommandDesc):
            output += ("\n  - - -  **{0}**  - - -  \n".format(module))
            for command in sorted(ShinobuCommandDesc[module]):
                desc = "No description provided"
                desc = ShinobuCommandDesc[module][command]
                output += (("." + command + "").ljust(10) + " - " + desc + "\n")
        await shinobu.send_message(message.channel, output + "")

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
        mods = shinobu.reload_all()
        await shinobu.edit_message(start, "Loaded {0} modules".format(mods))

    @ShinobuCommand("Tells Shinobu to load or reload a specified module")
    async def load(message: discord.Message, arguments: str):

        if not shinobu.author_is_owner(message):
            await shinobu.send_message(message.channel, ">tries to load mod\n>isn't owner")
            return
        start = await shinobu.send_message(message.channel, "Loading module {0}".format(arguments))
        if shinobu.reload_module(arguments):
            text = "Loaded module {0}"
        else:
            text = "Failed loading module {0}"
        await shinobu.edit_message(start, text.format(arguments))

    @ShinobuCommand("Tells Shinobu to load or reload a specified module")
    async def unload(message: discord.Message, arguments: str):

        if not author_is_owner(message):
            await shinobu.send_message(message.channel, ">tries to load mod\n>isn't owner")
            return
        start = await shinobu.send_message(message.channel, "Unloading module {0}".format(arguments))
        if shinobu.unload_mod(arguments):
            text = "Unloaded module {0}"
        else:
            text = "Failed unloading module {0}"
        await shinobu.edit_message(start, text.format(arguments))

    @ShinobuCommand("Pulls latest from the ShinobuBot repo")
    async def fetch(message: discord.Message, arguments: str):
        from subprocess import check_output
        out = check_output(["git", "pull"]).decode("utf-8")
        await shinobu.send_message(message.channel, out)

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

version = "1.0.1"
shinobu = None
