import discord
from resources import *
from math import floor
from random import random
import ShinobuTextBasedResponses
import ShinobuCommands
from ShinobuCommands import ShinobuCommandList
owner_id = "142860170261692416"

status = False
shinobu = ShinobuCommands.get_instance()

# print(ShinobuCommandList)

async def on_mention(message: discord.Message):
    words = message.content.rsplit(" ")
    global status
    for word in words:
        if word.startswith("<@"):
            words.remove(word)
            break
    if len(words) > 0 and status is False:
        command = words[0].lower()
        print("MENTION:", command)
        if command == "pat":
            await shinobu.send_message(message.channel, choose_random(shinobu_pat))
        elif command == "leave":
            if not author_is_owner(message):
                return
            await shinobu.send_message(message.channel, shinobu_exit)
            status = True
        elif command == "donut":
            await shinobu.send_message(message.channel, choose_random(shinobu_eat_donut))

        elif command.lower().startswith("he") or command.lower().startswith("hi"):
            if "Xsitsu" in message.author.name:
                name = "fag lord"
            else:
                name = "<@" +message.author.id+">"
            await shinobu.send_message(message.channel, choose_random(shinobu_greeting) + name)

        else:
            await shinobu.send_message(message.channel, shinobu_sit)
    else:
        command = words[0].lower()
        if command is "return":
            status = False
            print("Back")
            # await shinobu.send_message(message.channel, "I'm back :3")

def author_is_owner(message):
    return message.author.id == owner_id

@ShinobuTextBasedResponses.BanePostBigGuy
@ShinobuTextBasedResponses.BanePost4U
@ShinobuTextBasedResponses.NiceMemer
@ShinobuTextBasedResponses.Thanks
@ShinobuTextBasedResponses.PairedResponse
def text_based_response(message:discord.Message):
    return None


@shinobu.event
async def on_ready():
    print('Logged in as:', shinobu.user.name)
    print('-------------------------')


@shinobu.event
async def on_message(message:discord.Message):
    global status
    print("[" + message.author.name +"]", "\n" + message.content)
    if message.author.id == shinobu.user.id: return;
    mention = False
    for user in message.mentions:
        if user.id == shinobu.user.id:
            mention = True
        break
    if mention:
        await on_mention(message)
    elif status is not True:
        if message.content[0] is not ".":
            response = text_based_response(message)
            print("Response:", response)
            if response is not None:
                await shinobu.send_message(message.channel, response)
        if author_is_owner(message):
            if message.content[0] == ".":
                command = message.content.rsplit(" ")[0][1:]
                arguments = message.content[len(command)+2:]
                print(command)
                if command in ShinobuCommandList:
                    await ShinobuCommandList[command](message, arguments)
                else:
                    print("Command not found")


shinobu.run('MjI3NzEwMjQ2MzM0NzU4OTEz.CsKHOA.-VMTRbjonKthatdxSldkcByan8M')