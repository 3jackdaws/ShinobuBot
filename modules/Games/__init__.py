from importlib import reload as reloadmod

from . import simple_games

simple_games = reloadmod(simple_games)
import Games.betting as betting
betting = reloadmod(betting)
import discord
from Shinobu.client import Shinobu
from Shinobu.annotations import *
import asyncio
from random import randint
import re

SHINOBU_PROTOCREDIT_RESERVE = 1



version = "1.0.0"
type = "Module"
Description = "Contains various game-related commands."


async def on_message(message:discord.Message):
    if message.channel.name != "shitpost-central":
        return
    num = randint(1,24)
    print(num)
    if num is 7:
        await shinobu.send_message(message.channel, "Congratulations!  You've been awarded a Protocredit.")
        if not betting.get_account(message.author.id):
            betting.add_account(message.author.id, message.author.name, 10)
        betting.transaction(SHINOBU_PROTOCREDIT_RESERVE, message.author.id, 1)



def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance
    db_connector = shinobu.db
    betting.set_db_mod(db_connector)
    betting.assure_tables()

shinobu = None # type: Shinobu

games = {
    "roll":simple_games.roll_dice,
    "flip":simple_games.flip
}


def register_commands(ShinobuCommand):
    @ShinobuCommand
    async def roll(message: discord.Message, arguments: str):
        roll.description = "Rolls N dice, by default, five."
        try:
            num_dice = int(arguments)
        except:
            num_dice = 5
        text, odds = simple_games.roll_dice(num_dice)
        await shinobu.send_message(message.channel, text)

    @ShinobuCommand
    async def flip(message: discord.Message, arguments: str):
        mes = await shinobu.send_message(message.channel, "Flipping a coin for {}.\n".format(arguments))
        await shinobu.send_typing(message.channel)
        text = ["Heads!", "Tails!"]
        f = randint(0, 1)
        await asyncio.sleep(1)
        await shinobu.send_message(message.channel, text[f])

    @ShinobuCommand
    async def top(message: discord.Message, arguments: str):
        limit = 10
        output = "Top 10 Balances:\n```"
        for row in betting.fetch_top_balances(limit):
            print(row["UserID"])
            member = message.server.get_member(str(row['UserID']))
            output+= "{:20} Balance: [{}]\n".format(member.nick, round(row['Balance'], 2))
        await shinobu.send_message(message.channel, output + "```")

    @ShinobuCommand
    async def store(message: discord.Message, arguments: str):
        output = "Items available:\n"
        for item in sorted(betting.config['store_items'], key=lambda x:x['name']):
            output+=item['name'] + " - " + item['price'] + "\n"
        await shinobu.send_message(message.channel, output)

    @ShinobuCommand
    async def bal(message: discord.Message, arguments: str):
        await shinobu.send_typing(message.channel)
        if arguments is "":
            user = message.author
        else:
            user = message.mentions[0]

        user_record = betting.get_account(user.id)
        print(user_record)
        if user_record is None:
            user = message.server.get_member(user.id)
            betting.add_account(user.id, user.name, 0)
            betting.transaction(SHINOBU_PROTOCREDIT_RESERVE, user.id, 10, "Enroll bonus")
            user_record = betting.get_account(user.id)
        await shinobu.send_message(message.channel, "<@{}> has {} protocredits.".format(user.id, round(user_record["Balance"], 2)))

    @ShinobuCommand
    async def bet(message: discord.Message, arguments: str):
        args = arguments.rsplit()
        try:
            amount = float(args[0])
        except:
            await shinobu.send_message(message.channel, "The first argument must be the amount you want to bet.")
            return
        try:
            game = args[1]
            global games
            if not game in games:
                await shinobu.send_message(message.channel, "Valid games are {}".format([x for x in games]))
                return
        except:
            shinobu.send_message(message.channel, "The second argument must be a game.")
            return
        if betting.transaction(message.author.id, SHINOBU_PROTOCREDIT_RESERVE, amount, "BET: {}, MESSAGE: {}".format(game, message.id)):
            await shinobu.send_message(message.channel, "Deducting {} protocredits.".format(amount))
            await shinobu.send_typing(message.channel)
            await asyncio.sleep(2)
            text, odds = games[game]()
            await shinobu.send_message(message.channel, text)
            winnings = (amount * odds) + amount

            betting.transaction(SHINOBU_PROTOCREDIT_RESERVE, message.author.id, winnings, "BET: WINNINGS")

            output = "<@{}> won back **{}** protocredits.".format(message.author.id, round(winnings, 2))
        else:
            output = "You don't have enough protocredits to bet."
        await shinobu.send_message(message.channel, output)

    @ShinobuCommand
    @usage(".transfer num @mention")
    async def transfer(message: discord.Message, arguments: str):
        args = arguments.rsplit()
        try:
            num = float(args[0])
            user = message.mentions[0]
            betting.transaction(message.author.id, user.id, num)
            await shinobu.send_message(message.channel, "<@{}> tranfered <@{}> {} protocredits.".format(message.author.id, user.id, num))
        except:
            pass

    @ShinobuCommand
    @usage(".credit num @mention1 @mention2")
    async def credit(message: discord.Message, arguments: str):
        args = arguments.rsplit()
        try:
            num = float(args[0])
            for user in message.mentions:
                if betting.transaction(SHINOBU_PROTOCREDIT_RESERVE, user.id, num):
                    await shinobu.send_message(message.channel, "<@{}> tranfered <@{}> {} protocredits.".format(shinobu.user.id, user.id, num))
        except:
            pass
