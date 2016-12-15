import discord
from Shinobu.client import Shinobu
import asyncio
from importlib import reload
import Administration.regex as regex
regex = reload(regex)
import re

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
    @ShinobuCommand(".filter pattern", permissions=("Shinobu Owner"))
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

        await shinobu.send_message(message.channel,
                                   "What is the name of this filter?")
        resp = await shinobu.wait_for_message(channel=message.channel, author=message.author)
        name = resp.content
        regex.create_filter(name, pattern, channels, users, response)

    @ShinobuCommand("Shows all filters.  .show_filters with channel_or_user_mention", blacklist=("shitpost-central"))
    async def show_filters(message: discord.Message, arguments: str):
        try:
            referencing = re.findall("with \<.([0-9]+)", message.content)[0]
        except:
            referencing = None
        print(referencing)

        for filter in regex.config["filters"]:
            if referencing is None or referencing in filter['users'] or referencing in filter['channels']:
                output = "\nName: {}\nPattern: {}\nChannels: ".format(filter['name'],filter['pattern'])
                for chan in filter['channels']:
                    output+= "<#{}> ".format(chan)
                output += "\nUsers: "
                for user in filter['users']:
                    output+= "<@{}>,".format(user)
                await shinobu.send_message(message.channel, output + "\n--\n")

    @ShinobuCommand(".remove_filter name", permissions=("Shinobu Owner"))
    async def remove_filter(message: discord.Message, arguments: str):
        for filter in regex.config["filters"]:
            if filter['name'] == arguments:
                regex.config['filters'].remove(filter)

