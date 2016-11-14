import discord
from classes.Shinobu import Shinobu
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
        await shinobu.send_message(message.channel, "*Tuturu!* Shinobu desu.\n[{0}]".format(shinobu.config["instance name"]))

    @ShinobuCommand("Posts the link to the documentation on Github")
    async def docs(message: discord.Message, arguments: str):
        await shinobu.send_message(message.channel, "Documentation is located at:\nhttps://github.com/3jackdaws/ShinobuBot/wiki/Full-Command-List")

    @ShinobuCommand("Posts the link to the documentation on Github")
    async def ban(message: discord.Message, arguments: str):
        if shinobu.author_is_owner(): return

        member_id = re.search("[0-9]+").group()[0]
        print(member_id)
        for member in shinobu.get_all_members():
            if member.id == member_id:
                shinobu.invoke(shinobu.ban(member, delete_message_days=0))

    @ShinobuCommand("Posts the link to the documentation on Github")
    async def kick(message: discord.Message, arguments: str):
        if not shinobu.author_is_owner(message): return
        member_id = re.search("[0-9]+", message.content).group()
        print(member_id)
        for member in shinobu.get_all_members():
            if member.id == member_id:
                print("Kicking ",member.name)
                shinobu.invoke(shinobu.kick(member))


