import discord
from classes.Shinobu import Shinobu
import asyncio
from importlib import reload
import Administration.regex as regex
regex = reload(regex)

version = "1.0.0"

async def accept_message(message:discord.Message):
    channel = message.channel
    response, delete = regex.content_filter(message)
    if delete:
        await shinobu.delete_message(message)
        if response:
            mes = await shinobu.send_message(channel, response)
            await asyncio.sleep(5)
            await shinobu.delete_message(mes)



def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

shinobu = None # type: Shinobu


def register_commands(ShinobuCommand):
    @ShinobuCommand(".filter pattern", ["owner"])
    async def filter(message: discord.Message, arguments: str):
        pattern = arguments
        if len(pattern) < 2:
            await shinobu.send_message(message.channel, "The filtered pattern must be more than 1 character")
            return
        channels = []
        users = []
        await shinobu.send_message(message.channel, "What channels should this filter apply to? \nType as mentions separated by spaces.")
        resp = await shinobu.wait_for_message(channel=message.channel, author=message.author)
        if "cancel" in resp.content:
            return

        for chan in resp.channel_mentions:
            channels.append(chan.id)

        await shinobu.send_message(message.channel,
                                   "Who should this filter apply to? \nType as mentions separated by spaces.")
        resp = await shinobu.wait_for_message(channel=message.channel, author=message.author)
        for user in resp.mentions:
            users.append(user.id)

        await shinobu.send_message(message.channel, "What should I say when I remove a message?  Type 'nothing' for no response.")
        resp = await shinobu.wait_for_message(channel=message.channel, author=message.author)
        response = None if resp.content.lower() == "nothing" else resp.content
        regex.create_filter(pattern, channels, users, response)





