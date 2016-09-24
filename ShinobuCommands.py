import discord
import resources

shinobu = discord.Client()

def get_instance():
    return shinobu

ShinobuCommandList = {}
ShinobuCommandDesc = {}



def ShinobuCommand(description):
    def find_command(command_function):
        ShinobuCommandList[command_function.__name__] = command_function
        ShinobuCommandDesc[command_function.__name__] = description
        return command_function
    return find_command

@ShinobuCommand("Lists all of the available commands")
async def commands(message:discord.Message, arguments:str):
    output = "```java\n"
    for command in ShinobuCommandList:
        desc = "No description provided"
        if command in ShinobuCommandDesc:
            desc = ShinobuCommandDesc[command]
        output+= (("\"" + command + "\"").ljust(10) + " - " + desc + "\n")
    await shinobu.send_message(message.channel, output + "```")

@ShinobuCommand("Echos the text after the command to the same channel")
async def echo(message:discord.Message, arguments:str):
    await shinobu.send_message(message.channel, arguments)

@ShinobuCommand("Announces a message in the default channel of all servers")
async def broadcast(message:discord.Message, arguments:str):
    for channel in shinobu.get_all_channels():
        if channel.is_default:
            await shinobu.send_message(channel, arguments)

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