import discord
from classes.Shinobu import Shinobu
from random import randint
import asyncio

async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

shinobu = None # type: Shinobu
version = "1.0.0"


def register_commands(ShinobuCommand):

    @ShinobuCommand("Rolls n dice. By default, five.", ["all"])
    async def roll(message: discord.Message, arguments: str):
        lookup = {
            1:":one:",
            2:":two:",
            3:":three:",
            4:":four:",
            5:":five:",
            6:":six:"
        }
        total = 0
        results = "**Total**: {}/{} [{}%]\n"
        try:
            num_dice = int(arguments)
        except:
            num_dice = 5
        if num_dice > 100 or num_dice < 1:
            await shinobu.send_message(message.channel, "You can only roll between 1 and 100 dice.")
            return
        count_dice = {
            1:0,
            2:0,
            3:0,
            4:0,
            5:0,
            6:0,
        }
        for i in range(0,num_dice):
            res = randint(1,6)
            count_dice[res] += 1
            total += res
            results += lookup[res]
        if num_dice == 5:
            pre = ""
            max_num = 0
            for key in count_dice:
                if count_dice[key] > max_num:
                    max_num = count_dice[key]
                    pre = "__{}__ of a kind!\n".format(lookup[max_num][1:-1].capitalize())
            if max_num > 1:
                results = pre + results
        max = 6 * num_dice
        percent = round((total/(max))*100)
        await shinobu.send_message(message.channel, results.format(total, max, percent))
        if percent > 85:
            say = "Exceptional Roll!"
        elif percent > 70:
            say = "Good Roll!"
        else:
            return
        await shinobu.send_message(message.channel, say)

    @ShinobuCommand("Flips a coin", ["all"])
    async def flip(message: discord.Message, arguments: str):
        if arguments == "":
            arguments = "fun"
        mes = await shinobu.send_message(message.channel, "Flipping a coin for {}.\n".format(arguments))
        await shinobu.send_typing(message.channel)
        text = ["Heads!\n","Tails!\n"]
        coin = ["<:heads:254844851823181826>",
                "<:tails:254844903886946306>"]
        f = randint(0,1)
        await asyncio.sleep(1)
        await shinobu.send_message(message.channel, text[f])

    @ShinobuCommand("Flips a coin", ["all"])
    async def farmptt(message: discord.Message, arguments: str):
        spb = None
        for mem in shinobu.get_all_members():
            if mem.id == "255139669577170954":
                spb = mem
        while 1:
            msg = await shinobu.wait_for_message(content="**BANG**")
            await shinobu.send_message(message.channel, "pull the trigger")