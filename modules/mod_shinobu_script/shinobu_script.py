import discord
import re
from Shinobu.client import Shinobu

def Channel(channel_name, server:discord.Server):
    for channel in server._channels:
        if channel.name == channel_name:
            return channel

class this:
    def __init__(self, message):
        self.channel = message.channel.name
        self.message = message.content
        self.author = message.author.name




def get_env(**kwargs):
    import mod_shinobu_script.environment as environment
    env = environment.__dict__
    for key in kwargs:
        env[key] = kwargs[key]
    env["this"] = this(env["message"])
    return env

def run(message, shinobu:Shinobu):
    import mod_shinobu_script.environment as environment
    code = parse(message)
    print(code)
    exec(code, get_env(message=message, shinobu=shinobu))

def parse(message:discord.Message):
    code = re.findall("(?<=```py)[\s\S]*?(?=```)", message.content)[0]
    gen = ""
    for line in code.rsplit("\n"):
        line = re.sub("\n", "", line)
        gen += "{}\n".format(line)
    return gen