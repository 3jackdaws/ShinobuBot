import discord
import re
import datetime
import asyncio

decode_periods = {"sec":1,
                  "min":60,
                  "hour":3600}

def get_seconds_from_str(period:str):
    total_seconds = 0
    for per in decode_periods:
        reg = "[0-9]+ (?="+per+")"
        multiplier = decode_periods[per]
        match = re.findall(reg, period)
        if match:
            time = re.findall("[0-9]+", match[0])[0]
            time_in_secs = multiplier * int(time)
            total_seconds+= time_in_secs
    return total_seconds


def register_commands(ShinobuCommand):
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

    @ShinobuCommand("Sets a reminder")
    async def remindme(message:discord.Message, arguments:str):
        arguments = arguments.lower()
        global reminder_list
        author = message.author.id
        if author not in reminder_list:
            reminder_list[author] = []
        time = re.search("(@)[0-9:]", arguments)
        relative = re.search("in",arguments) is not None
        if relative:
            period = re.findall("(in) ([ a-z0-9]+)(\"| to|$)", arguments)
            text = re.findall("(to|\") ([ a-z0-9]+?)(\"| in|$)", arguments)

            if period:
                period = period[0][1]
            if text:
                text = text[0][1]
            time_til = get_seconds_from_str(period)

            start_reminder(time_til, author, text)

            if author not in timer_list:
                timer_list[author] = []
            # timer_list[author].append(s)
            now = datetime.datetime.now()
            now_offset = now + datetime.timedelta(seconds=time_til)
            reminder_list[author].append([now_offset.timestamp(), text])
            datestring = now_offset.strftime("%-I:%M:%S%p on %b %-d, %Y")
            await shinobu.send_message(message.channel, "Reminded scheduled for {0}".format(datestring))
            write_reminder()



async def accept_message(message:discord.Message):
    pass


def accept_shinobu_instance(i:discord.Client):
    global shinobu

    shinobu = i
    read_reminder()

def read_reminder():
    global reminder_list
    import json
    reminder_file = open("resources/reminder_list.json", "a+")
    reminder_file.seek(0)
    try:
        reminder_list = json.load(reminder_file)
    except json.decoder.JSONDecodeError as e:
        reminder_list = {}
    for member in reminder_list:
        for reminder in reminder_list[member]:
            time = float(reminder[0]) - datetime.datetime.now().timestamp()
            if time < 0:
                reminder_list[member].remove(reminder)
                continue
            author = member

            start_reminder(time, author, reminder[1])
    write_reminder()


def write_reminder():
    global reminder_list
    import json
    reminder_file = open("resources/reminder_list.json", "w")
    json.dump(reminder_list, reminder_file)


def start_reminder(time, authorid, text):
    async def send_message():
        author = None
        for user in shinobu.get_all_members():
            if user.id == authorid:
                author = user
                break
        await asyncio.sleep(time)
        await shinobu.send_message(author, "***Reminder:***\n{0}" .format(text))
        print("Sending scheduled message to {0}".format(author.nick))

    fut = asyncio.ensure_future(send_message())


shinobu = None
version = "0.0.1"
reminder_list = {}
timer_list = {}
