import discord
from logging import Logger
import datetime
import inspect

async def on_message(message:discord.Message):
    time = datetime.datetime.now().strftime("%b %d, %Y - %H:%I:%S")
    log("\033[36m{}\033[0m - {}\n{}\n".format(message.author.name, time, message.content), channel=message.channel.name)

def register_commands(ShinobuCommand):
    pass

def accept_shinobu_instance(i):
    i.log = log

version = "1.0.4"
type = "Module"
Description = "Logs server messages and command output"
log_file = open("resources/serverlog.log", "a+", 1)
last_channel = None

def log(msg, *args, channel=None):
    global log_file, last_channel
    log_line = ""
    if not channel:
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0]).__name__
    else:
        if not channel == last_channel:
            log_line += "\033[31m[[[    {}    ]]]\033[0m\n".format(channel)
            last_channel = channel
    time = datetime.datetime.now().strftime("%H:%I:%S")

    if channel:
        log_line += msg
    else:
        log_line += "[{}][{}] {}".format(time, mod, msg)
    print(log_line)
    log_file.write(log_line + "\n")

def cleanup():
    log_file.close()