from classes.utility import ConfigManager
import discord
import re

config = ConfigManager("resources/administration/regex.json")

config.assure("filters", [])

for filter in config["filters"]:
    print(print(filter))

def create_filter(pattern, channels, on_delete):
    filter = {
        "pattern":pattern,
        "channels":channels,
        "on_delete":on_delete
    }
    if filter not in config["filters"]:
        config["filters"].append(filter)

def content_filter(message:discord.Message):
    text = message.content
    channel_id = message.channel.id
    for filter in config['filters']:
        if channel_id in filter['channels']:
            pattern = "(^|[^a-z])" + filter['pattern'] + "($|[^a-z])"
            if re.search(pattern, text):
                return filter['on_delete'], True
    return None, False
