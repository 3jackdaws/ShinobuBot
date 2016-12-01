import discord
import re
import datetime
import asyncio
import os
from classes.Shinobu import Shinobu
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

def init_reminders():
    global reminders, reminder_count
    stored_reminders = json.load(open(shinobu.config_directory + "reminders.json"))
    for reminder in stored_reminders:
        id = reminder["id"]
        if reminder_count < id: reminder_count = id
        queue_reminder(reminder)

def write_reminders():
    global reminders
    file = open(shinobu.config_directory + "reminders.json", "w+")
    json.dump(reminders, file, indent=2)



def register_commands(ShinobuCommand):
    @ShinobuCommand("Schedule a message: .schedule \"message\" for [me|@mention|#channel] [single|repeat [daily|weekly|monthly]] [8:00PM]")
    async def schedule(message: discord.Message, arguments: str):
        text = re.findall("\"(.+)\"", arguments)[0]
        multiple = re.findall("(single|repeat)", arguments)[0]
        frequency = None
        if multiple == "repeat":
            frequency = re.findall("(daily|weekly|monthly)", arguments)
        time = re.search("([:0-9]+(am|pm))", arguments.lower()).group()
        who = re.findall("for ([@#\<\>!0-9]+)", arguments)[0]
        to = get_channel_object(who)
        if to is None:
            await shinobu.send_message(message.channel, "I could not find {}".format(who))
        else:
            print(datetime.datetime.strptime(time))
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



    @ShinobuCommand("Shows all scheduled reminder_list")
    async def reminders(message:discord.Message, arguments:str):
        global reminder_list
        output = "**Reminders for <@{0}>**\n".format(message.author.id)
        if message.author.id not in reminder_list:
            output = "You have no scheduled reminders"
        else:
            for reminder in reminder_list[message.author.id]:
                # print(reminder[0].microsecond)
                datestring = datetime.datetime.fromtimestamp(reminder[0]).strftime("%-I:%M:%S%p on %b %-d, %Y")
                output += "__{0}__ - {1}\n".format(reminder[1], datestring)
        await shinobu.send_message(message.channel, output)



def accept_shinobu_instance(i:discord.Client):
    global shinobu
    shinobu = i
    init_reminders()



shinobu = None #type: Shinobu
version = "0.0.1"
reminders = []
reminder_count = 0

