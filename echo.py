import discord

async def accept_message(message:discord.Message):
    await shinobu.send_message(message.channel, message.content)

def accept_shinobu_instance(i:discord.Client):
    global shinobu
    shinobu = i


version = "1.0.2"