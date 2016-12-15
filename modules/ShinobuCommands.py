import discord
from Shinobu.client import Shinobu
import resources
import glob
import os
import re
import json
import time
from urllib.request import urlopen
import asyncio
from math import floor
from Shinobu.utility import ConfigManager
version = "1.2.7"



async def accept_message(message:discord.Message):
    reset_channel_timeout(message.channel.id)

def cleanup():
    global prune_loop
    if hasattr(prune_loop, "cancel"):
        print("Stopping prune loop")
        prune_loop.cancel()


async def prune_temp_channels():
    while 1:
        check_frequency = int(config["check_frequency"])
        await asyncio.sleep(check_frequency)
        now = int(time.time())
        warn_time = int(config['warn_time'])
        for channel in config["temp_channels"]:
            expires = int(channel['expires'])
            warn_at = channel['warn']
            if now > expires:
                print("Delete Channel")
                await shinobu.delete_channel(shinobu.get_channel(channel['id']))
                config["temp_channels"].remove(channel)
            elif warn_at and warn_at > now:
                channel['warn'] = None
                await shinobu.send_message(shinobu.get_channel(channel['id']), "This channel will soon be pruned due to inactivity")

def accept_shinobu_instance(instance):
    global shinobu, prune_loop
    shinobu = instance
    prune_loop = shinobu.invoke(prune_temp_channels())

def reset_channel_timeout(channelid):
    global config
    for channel in config["temp_channels"]:
        if channel['id'] == channelid:
            print("Reset channel timeout for {}".format(channel['name']))
            channel['expires'] = int(time.time()) + int(config['prune_after_seconds'])


shinobu = None # type: Shinobu
config = ConfigManager("resources/ShinobuCommands.json")
config.assure("temp_channels", [])
config.assure("check_frequency", 600)
config.assure("prune_after_seconds", 3600*24)
config.assure("warn_time", 600)
config.assure("reichlist", [])

prune_loop = None # type: asyncio.futures.Future



def register_commands(ShinobuCommand):


    @ShinobuCommand("Announces a message in the default channel of all servers", permissions = ("Shinobu Owner"), whitelist=("bot-shitposting"))
    async def broadcast(message:discord.Message, arguments:str):
        if not shinobu.author_is_owner(message):
            return
        for channel in shinobu.get_all_channels():
            if channel.is_default:
                await shinobu.send_message(channel, arguments)

    @ShinobuCommand("Posts a message in a channel that a user doesn't have access to", blacklist=("shitpost-central"))
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
        if not shinobu.author_is_owner(): return

        member_id = re.search("[0-9]+").group()[0]
        print(member_id)
        for member in shinobu.get_all_members():
            if member.id == member_id:
                shinobu.invoke(shinobu.ban(member, delete_message_days=0))

    @ShinobuCommand("Posts the link to the documentation on Github", permissions = ("Shinobu Owner"), whitelist=("bot-shitposting"))
    async def kick(message: discord.Message, arguments: str):
        if not shinobu.author_is_owner(message): return
        member_id = re.search("[0-9]+", message.content).group()
        print(member_id)
        for member in shinobu.get_all_members():
            if member.id == member_id:
                print("Kicking ",member.name)
                shinobu.invoke(shinobu.kick(member))

    @ShinobuCommand("Gets the current weather for Klamath Falls")
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

    @ShinobuCommand(".purge @mention til_message_id", permissions = ("Shinobu Owner"))
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

    @ShinobuCommand(".temp channel_name @mentions_who_can_join")
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
        await shinobu.edit_channel(channel, topic="Temporary channel")
        global config
        expires = int(time.time()) + int(config["prune_after_seconds"])
        config["temp_channels"].append({
            "id":channel.id,
            "name":channel.name,
            "expires":expires,
            "warn":expires - int(config['warn_time']),
            "creator":message.author.id
        })

    @ShinobuCommand("Adds a text entry to the reichlist")
    async def reichlist(message: discord.Message, arguments: str):
        try:
            args = arguments.rsplit(" ")
            subcommand = args[0]
            if subcommand == "add":

                text = re.findall("(?<=\").+?(?=\")", arguments)[0]
                config['reichlist'].append(text)
                await shinobu.send_message(message.channel, "Added to list")
            elif subcommand == "show":
                output = ""
                for item in config['reichlist']:
                    output+= item + "\n"
                await shinobu.send_message(message.channel, output)
        except:
            pass

