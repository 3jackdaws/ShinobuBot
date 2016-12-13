import discord
import re
import datetime
import asyncio
import os
from Shinobu.client import Shinobu
import json

os.environ['TZ'] = 'America/Los_Angeles'

def queue_reminder(reminder):
    global reminders, reminder_count
    reminder_count += 1
    reminder["id"] = reminder_count
    if schedule_reminder(reminder):
        reminders.append(reminder)

def delete_reminder(id):
    global reminders
    for reminder in reminders:
        if reminder["id"] == id:
            reminders.remove(reminder)
            write_reminders()

def schedule_reminder(reminder):
    delta = calc_second_offset(reminder["time"])
    if delta < 0:
        delta += (60*60*24)
    channel = get_channel_object(reminder["to"])
    if channel is not None:
        print("Scheduling Reminder - Delta [{}]".format(delta))
        async def send_reminder():
            await asyncio.sleep(delta)
            print("Sending message")
            await shinobu.send_message(channel, reminder["message"])
            if reminder['frequency'] is None:
                delete_reminder(reminder["id"])
        shinobu.invoke(send_reminder())
        return True
    return False

def get_channel_object(tag:str):
    id = re.search("[0-9]+", tag).group()
    if "#" in tag:
        return shinobu.get_channel(id)
    elif "@" in tag:
        for member in shinobu.get_all_members():
            if member.id == id:
                return member
    return None


def calc_second_offset(time):
    now = datetime.datetime.strptime(datetime.datetime.now().strftime("%I:%M%p"), "%I:%M%p")
    alert = datetime.datetime.strptime(time, "%I:%M%p")
    return (alert - now).total_seconds()

def screen_message(text, author):
    commands = re.findall("![a-z_]+", text)
    for comm in commands:
        com_dict = shinobu.get_command(comm[1:])
        if "permissions" in com_dict:
            if not shinobu.can_exec(author, shinobu.get_command(comm[1:])):
                return comm
    return None

def init_reminders():
    global reminders, reminder_count
    stored_reminders = json.load(open(shinobu.config_directory + "reminders.json"))
    for reminder in stored_reminders:
        id = reminder["id"]
        if reminder_count < id:
            reminder_count = id
        queue_reminder(reminder)

def write_reminders():
    global reminders
    file = open(shinobu.config_directory + "reminders.json", "w+")
    json.dump(reminders, file, indent=2)



def register_commands(ShinobuCommand):
    @ShinobuCommand("", ["all"])
    async def test(message: discord.Message, arguments: str):
        screen_message(arguments)

    @ShinobuCommand("Schedule a message: .schedule \"message\" for [me|@mention|#channel] [single|repeat [daily|weekly|monthly]] [8:00PM]", ["all"])
    async def schedule(message: discord.Message, arguments: str):
        text = re.findall("\"(.+)\"", arguments)[0]
        try:
            multiple = re.findall("(single|repeat)", arguments)[0]
        except:
            multiple = "single"
        frequency = None
        if multiple == "repeat":
            frequency = re.findall("(daily|weekly|monthly)", arguments)
        time = re.search("([:0-9]+(am|pm))", arguments.lower()).group()
        who = re.findall("for ([@#\<\>!0-9]+)", arguments)[0]
        to = get_channel_object(who)
        bad_command = screen_message(text, message.author)
        if to is None:
            await shinobu.send_message(message.channel, "I could not find {}".format(who))
        elif bad_command is not None:
            await shinobu.send_message(message.channel, "You are not allowed to use the {} command.".format(bad_command))
        else:
            # print(datetime.datetime.strptime(time))
            reminder = {
                "message": text,
                "time": time,
                'frequency': frequency,
                "to": who,
                "thread":None,
                "author_id":message.author.id
            }
            queue_reminder(reminder)
            write_reminders()



    @ShinobuCommand("Shows all scheduled reminders", ['all'])
    async def reminders(message:discord.Message, arguments:str):
        global reminders
        output = "**Reminders for <@{0}>**\n".format(message.author.id)
        for reminder in reminders:
            if reminder["author_id"] == message.author.id:
                output+="\"{}\" for {} at {}\n".format(reminder['message'], reminder['to'], reminder["time"])
        await shinobu.send_message(message.channel, output)



def accept_shinobu_instance(i:discord.Client):
    global shinobu
    shinobu = i
    init_reminders()



shinobu = None #type: Shinobu
version = "0.0.1"
reminders = []
reminder_count = 0

