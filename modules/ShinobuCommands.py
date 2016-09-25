import discord
import resources

version = "1.1.0"

async def accept_message(message:discord.Message):
    if message.content[0] is ".":
        command = message.content.rsplit(" ")[0][1:]
        arguments = " ".join(message.content.rsplit(" ")[1:])
        # print("COMMAND: {0}, ARGUMENTS: {1}".format(command, arguments))
        if command in ShinobuCommandList:
            await ShinobuCommandList[command](message, arguments)

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance


shinobu = None
ShinobuCommandList = {}
ShinobuCommandDesc = {}



def ShinobuCommand(description):
    global ShinobuCommandList
    global ShinobuCommandDesc
    def find_command(command_function):
        ShinobuCommandList[command_function.__name__] = command_function
        ShinobuCommandDesc[command_function.__name__] = description
        return command_function
    return find_command

def author_is_owner(message):
    return message.author.id == shinobu.owner

@ShinobuCommand("Lists all of the available commands")
async def commands(message:discord.Message, arguments:str):
    output = ""
    for command in sorted(ShinobuCommandList):
        desc = "No description provided"
        if command in ShinobuCommandDesc:
            desc = ShinobuCommandDesc[command]
        output+= (("`" + command + "`").ljust(10) + " - " + desc + "\n")
    await shinobu.send_message(message.channel, output + "")

@ShinobuCommand("Echos the text after the command to the same channel")
async def echo(message:discord.Message, arguments:str):
    await shinobu.send_message(message.channel, arguments)

@ShinobuCommand("Announces a message in the default channel of all servers")
async def broadcast(message:discord.Message, arguments:str):
    for channel in shinobu.get_all_channels():
        if channel.is_default:
            await shinobu.send_message(channel, arguments)

@ShinobuCommand("Lists all loaded modules")
async def modules(message:discord.Message, arguments:str):
    output = ""
    for module in shinobu.loaded_modules:
        output += ("**{0}** - Version {1}\n".format(module.__name__, module.version))
    await shinobu.send_message(message.channel, output)

@ShinobuCommand("Tells Shinobu to learn a paired response")
async def learn(message:discord.Message, arguments:str):
    print(arguments)
    components = arguments.split("|")
    if len(components) < 2:
        await shinobu.send_message(message.channel, "What is that supposed to mean?  You have to have a component I'm looking for and a component I respond with.  Those need to be separated by a pipe symbol '|'")
    else:
        if components[0] not in resources.pair_response:
            resources.pair_response[components[0]] = []
        resources.pair_response[components[0]].append(components[1])
        resources.write_pr()

@ShinobuCommand("Tells Shinobu to unlearn a paired response")
async def unlearn(message:discord.Message, arguments:str):
    if arguments in resources.pair_response:
        del resources.pair_response[arguments]
    resources.write_pr()

@ShinobuCommand("Tells Shinobu to unlearn a paired response and never learn it again")
async def block(message:discord.Message, arguments:str):
    if arguments in resources.pair_response:
        resources.pair_response[arguments] = None
    resources.write_pr()

@ShinobuCommand("Posts a message in a channel that a user doesn't have access to")
async def tell(message:discord.Message, arguments:str):
    originating_server = message.server
    given_message = message.content.rsplit(" ")[2:]
    sender = message.author.id
    for channel in message.channel_mentions:
        await shinobu.send_message(channel, ("<@"+sender + "> says:\n") + " ".join(given_message))

@ShinobuCommand("Tells Shinobu to reload her configuration")
async def reload(message:discord.Message, arguments:str):
    if not author_is_owner(message):
        await shinobu.send_message(message.channel, ">tries to reload config\n>isn't owner\n>mfw no face")
        return
    start = await shinobu.send_message(message.channel, "Reloading config")
    mods = shinobu.load_config()
    await shinobu.edit_message(start, "Loaded {0} modules".format(mods))

@ShinobuCommand("Tells Shinobu to load or reload a specified module")
async def load(message:discord.Message, arguments:str):
    if not author_is_owner(message):
        await shinobu.send_message(message.channel, ">tries to load mod\n>isn't owner")
        return
    start = await shinobu.send_message(message.channel, "Loading module {0}".format(arguments))
    if shinobu.load_mod(arguments):
        text = "Loaded module {0}"
    else:
        text = "Failed loading module {0}"
    await shinobu.edit_message(start, text.format(arguments))

@ShinobuCommand("Tells Shinobu to load or reload a specified module")
async def unload(message:discord.Message, arguments:str):
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
async def fetch(message:discord.Message, arguments:str):
    from subprocess import check_output
    out = check_output(["git", "pull"]).decode("utf-8")
    await shinobu.send_message(message.channel, out)
