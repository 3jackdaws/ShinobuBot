import discord

async def accept_message(message:discord.Message):
    print("------" + message.author.name + "------", "\n" + message.content + "\n")

def register_commands(ShinobuCommand):
    pass

def accept_shinobu_instance(i):
    pass

version = "1.0.1"