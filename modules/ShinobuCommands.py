import discord
from Shinobu.client import Shinobu
import resources
import glob
import os
import re
import json
from urllib.request import urlopen
import asyncio
from math import floor
version = "1.2.7"

async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

shinobu = None # type: Shinobu
temp_channels = []

def cleanup():
    global temp_channels
    for channel in temp_channels:
        shinobu.invoke(shinobu.delete_channel(channel))

def register_commands(ShinobuCommand):
    @ShinobuCommand("Rolls n dice. By default, five.", ["all"])
    async def chars(message: discord.Message, arguments: str):
        print(message.content.encode("utf-8"))
        await shinobu.send_message(message.channel, re.sub("!([a-z])", "\1", arguments))

    @ShinobuCommand("Announces a message in the default channel of all servers")
    async def broadcast(message:discord.Message, arguments:str):
        if not shinobu.author_is_owner(message):
            return
        for channel in shinobu.get_all_channels():
            if channel.is_default:
                await shinobu.send_message(channel, arguments)

    @ShinobuCommand("Posts a message in a channel that a user doesn't have access to", ['all'])
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

    @ShinobuCommand("All channels on the server", ["all"])
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

    @ShinobuCommand("Says what system Shinobu is running on", ['all'])
    async def who(message: discord.Message, arguments: str):
        await shinobu.send_message(message.channel, "*Tuturu!* Shinobu desu.\n[{0}]".format(shinobu.config["instance name"]))

    @ShinobuCommand("Posts the link to the documentation on Github", ["all"])
    async def docs(message: discord.Message, arguments: str):
        await shinobu.send_message(message.channel, "Documentation is located at:\nhttps://github.com/3jackdaws/ShinobuBot/wiki/Full-Command-List")

    @ShinobuCommand("Posts the link to the documentation on Github")
    async def ban(message: discord.Message, arguments: str):
        if not shinobu.author_is_owner(): return

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

    @ShinobuCommand("Gets the current weather for Klamath Falls", ["all"])
    async def weather(message: discord.Message, arguments: str):
        got_json = False
        while not got_json:
            url = "http://api.wunderground.com/api/{}/geolookup/conditions/q/OR/Klamath_Falls.json".format(shinobu.config['wu_token'])
            site_text = urlopen(url).read().decode("utf-8")
            kf_json = json.loads(site_text)
            try:
                weath = kf_json["current_observation"]["weather"]
                temp = kf_json["current_observation"]["temp_f"]
                got_json = True

                emoji = ""
                if "rain" in weath.lower():
                    emoji = ":cloud_rain:"
                elif "overcast" in weath.lower():
                    emoji = ":cloud:"
                elif "clear" in weath.lower():
                    emoji = ":cityscape:"
                elif "sunny" in weath.lower():
                    emoji = ":sunny:"
                await shinobu.send_message(message.channel, "**Klamath Falls, OR**\n{0} {1} {0}\n{2}°F".format(emoji, weath, round(temp)))
            except:
                pass

    @ShinobuCommand("Spam")
    async def spam(message: discord.Message, arguments: str):
        try:
            person = message.mentions[0]
            try:
                amount = arguments.rsplit()[0]
            except:
                amount = 10
            for i in range(amount):
                await asyncio.sleep(1)
                await shinobu.send_message(message.channel, arguments)
        except:
            pass

    @ShinobuCommand("Posts the link to the documentation on Github")
    async def config(message: discord.Message, arguments: str):
        key = arguments.rsplit()[0]
        value = json.loads("".join(arguments.rsplit()[1:]))
        shinobu.config[key] = value
        await shinobu.send_message(message.channel, "Changed property {} to {}".format(key, str(shinobu.config[key])))
        shinobu.write_config()

    @ShinobuCommand(".purge @mention til_message_id")
    async def purge(message: discord.Message, arguments: str):
        if shinobu.author_is_owner(message):
            args = arguments.rsplit()
            print("Purging")
            channel = message.channel
            who = args[0]
            ref = args[1]
            if who == "@everyone":
                def is_after(m):
                    return m.id > args[1]
            else:
                try:
                    who = message.mentions[0]
                except:
                    await shinobu.send_message(message.channel, "The second parameter must be a mention or everyone.")
                    return
                def is_after(m):
                    user = message.mentions[0]
                    return user == m.author and m.id > ref

            num_del = len(await shinobu.purge_from(channel, check=is_after))
            mes = await shinobu.send_message(message.channel, "Deleted {} messages.".format(num_del))
            await asyncio.sleep(2)
            await shinobu.delete_message(mes)

    @ShinobuCommand(".temp channel_name @mentions_who_can_join", ["all"])
    async def temp_channel(message: discord.Message, arguments: str):
        server = message.server
        args = arguments.rsplit()
        everyone_perms = discord.PermissionOverwrite(read_messages=False)
        member_perms = discord.PermissionOverwrite(read_messages=True, manage_channels=True)
        everyone = discord.ChannelPermissions(target=server.default_role, overwrite=everyone_perms)

        access = [discord.ChannelPermissions(target=message.author, overwrite=member_perms), everyone]
        for person in message.mentions:
            access.append(discord.ChannelPermissions(target=person, overwrite=member_perms))
        channel = await shinobu.create_channel(server, args[0], *access)
        global temp_channels
        temp_channels.append(channel)



