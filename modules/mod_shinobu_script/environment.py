import re
import discord
from Shinobu.client import Shinobu
from time import sleep

shinobu = None
message = None


def Send(chan, text):
    for channel in message.server.channels:
        if channel.name == chan:
            shinobu.quick_send(channel, text)
    return False
