import discord
import resources
import glob
import os
import re
version = "1.2.7"

async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

shinobu = None # type: discord.Client

def register_commands(ShinobuCommand):
    @ShinobuCommand("Echos the text after the command to the same channel")
    async def echo(message:discord.Message, arguments:str):
        await shinobu.send_message(message.channel, arguments)

    @ShinobuCommand("Announces a message in the default channel of all servers")
    async def broadcast(message:discord.Message, arguments:str):
        if not shinobu.author_is_owner(message):
            return
        for channel in shinobu.get_all_channels():
            if channel.is_default:
                await shinobu.send_message(channel, arguments)

    @ShinobuCommand("Posts a message in a channel that a user doesn't have access to")
    async def tell(message:discord.Message, arguments:str):
        originating_server = message.server
        given_message = arguments.rsplit(" ")[1:]
        requested_channel = arguments.rsplit(" ")[0]
        sender = message.author.id
        for channel in message.server.channels:
            if channel.name == requested_channel:
                await shinobu.send_message(channel, ("<@"+sender + "> told me to say:\n") + " ".join(given_message), tts=True)
                await shinobu.send_message(message.channel, "Sent message to {}".format(channel.name))
                return
        await shinobu.send_message(message.channel, "Could not find channel {}".format(requested_channel))

    @ShinobuCommand("All channels on the server")
    async def channels(message: discord.Message, arguments: str):
        output = "**Channels on this server:**\n__Text__\n"
        for channel in message.server.channels:
            if channel.type is discord.ChannelType.text:
                output += (channel.name + "\n")
        output += "\n__Voice__\n"
        for channel in message.server.channels:
            if channel.type is discord.ChannelType.voice:
                output += (channel.name + "\n")
        await shinobu.send_message(message.channel, output)

    @ShinobuCommand("Says what system Shinobu is running on")
    async def who(message: discord.Message, arguments: str):
        await shinobu.send_message(message.channel, "ShinobuBot on {0}".format(shinobu.config["instance name"]))

    @ShinobuCommand("Modifies config")
    async def setoption(message: discord.Message, arguments: str):
        option = arguments.rsplit(" ")[0]
        value = re.search("'[\s\S]+?'", arguments)
        if option in shinobu.config:
            shinobu.config[option] = value
        await shinobu.send_message(message.channel, "Config option '{}' set to '{}'".format(option, value))

    @ShinobuCommand("Modifies config")
    async def selectopt(message: discord.Message, arguments: str):
        pass

    @ShinobuCommand("Invites Shinobu to your server")
    async def invite(message: discord.Message, arguments: str):
        shinobu.accept_invite


    # @ShinobuCommand("Purges messages according to arguments provided")
    # async def purge(message: discord.Message, arguments: str):
    #     user=re.findall("(?<=user=)\<@[0-9]+\>", arguments)
    #     pattern = re.findall("(?<=pattern=)\"[\s\S]+\"", arguments)
    #     limit = re.findall("(?<=limit=)[0-9]+", arguments)
    #     nodelete = re.search(" nodelete", arguments) is not None
    #     channel = message.channel
    #     limit = int(limit)
    #     check = None
    #     if pattern is not None:
    #         check=lambda x:re.search(pattern, x) is not None
    #     await shinobu.purge_from(channel, check=check,limit=limit)
