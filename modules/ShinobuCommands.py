import discord
import resources
import glob
import os
version = "1.2.7"

async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

shinobu = None

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
        given_message = message.content.rsplit(" ")[2:]
        sender = message.author.id
        for channel in message.channel_mentions:
            await shinobu.send_message(channel, ("<@"+sender + "> told me to say:\n") + " ".join(given_message), tts=True)

    @ShinobuCommand("Says what system Shinobu is running on")
    async def who(message: discord.Message, arguments: str):
        from socket import gethostname
        await shinobu.send_message(message.channel, "ShinobuBot on {0}".format(gethostname()))
