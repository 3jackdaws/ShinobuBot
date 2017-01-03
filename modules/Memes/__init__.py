
from Shinobu.client import Shinobu
from Shinobu.annotations import *
import discord
import re
from .memes import is_meme as check_meme, get_trend, average_rows, get_meme



shinobu = None # type: Shinobu
type = "Module"
version = "1.0.0"





def accept_shinobu_instance(i):
    global shinobu
    shinobu = i

def register_commands(ShinobuCommand):
    @ShinobuCommand
    @description("The definitive guide to meme checking.  Checks if the argument string is classified as a meme.")
    @usage(".is_meme Milhouse")
    async def is_meme(message: discord.Message, arguments: str):
        if check_meme(arguments):
            await shinobu.send_message(message.channel, "__{}__ **IS** a meme.".format(arguments))
        else:
            await shinobu.send_message(message.channel, "__{}__ **IS NOT** a meme.".format(arguments))


    @ShinobuCommand
    @description("Gives a specific meme a popularity rating.")
    @usage(".rate \"Pepe the Frog\"")
    async def rate(message: discord.Message, arguments: str):
        await shinobu.send_typing(message.channel)
        meme_str = re.findall("(?<=\")[^\"^\n]{2,}(?=\")", arguments)
        true_memes = []
        for meme in meme_str:
            if not check_meme(meme):
                await shinobu.send_message(message.channel, "{} is not classified as a meme and cannot be rated.".format(meme))
            else:
                true_memes.append(meme)
        obj = get_trend(["4chan", *true_memes], "14-d")
        avg = average_rows(obj)
        output = ""
        for i,m in enumerate(avg):
            print(i, m['name'])
            if i > 1:
                output+= "{} - {}\n".format(m["name"], round(m["avg"], 2))
        await shinobu.send_message(message.channel, output)

    @ShinobuCommand
    @description("The definitive guide to meme checking.  Checks if the argument string is classified as a meme.")
    @usage(".findmeme milhouse")
    async def findmeme(message: discord.Message, arguments: str):
        await shinobu.send_message(message.channel, get_meme(arguments))

    @ShinobuCommand
    @description("The definitive guide to meme checking.  Checks if the argument string is classified as a meme.")
    @usage(".deviation \"milhouse\" \"other meme\"")
    async def deviation(message: discord.Message, arguments: str):
        await shinobu.send_message(message.channel, get_meme(arguments))