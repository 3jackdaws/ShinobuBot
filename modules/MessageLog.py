import discord
from logging import Logger
import datetime

async def accept_message(message:discord.Message):
    log(message.channel.name, "{}: {}".format(message.author.name, message.content))

def register_commands(ShinobuCommand):
    pass

def accept_shinobu_instance(i):
    pass

version = "1.0.4"
type = "Module"
Description = "Logs server messages and command output"
log_file = open("resources/serverlog.log", "a+")

def log(module, msg):
    global log_file
    time = datetime.datetime.now().strftime("%H:%I:%S")
    log_line = "[{}][{}] {}\n".format(time, module, msg)
    print(log_line)
    log_file.write(log_line)

def cleanup():
    log_file.close()