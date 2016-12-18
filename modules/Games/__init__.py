from importlib import reload as reloadmod
import Games.simple_games as simple_games
simple_games = reloadmod(simple_games)
import Games.betting as betting
from .database import Account
betting = reloadmod(betting)
import discord
from Shinobu.client import Shinobu
from Shinobu.annotations import *
import asyncio
from math import floor, trunc
from random import randint

SHINOBU_PROTOCREDIT_RESERVE = 1





version = "1.0.0"
type = "Module"



async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance
    db_connector = [x for x in shinobu.get_modules(type="connector") if x.__name__ == "connector_db"][0]
    betting.set_db_mod(db_connector)
    print(betting.db)
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
            user_id = message.author.id
        else:
            user_id = message.mentions[0].id
        try:
            user_record = Account(user_id)
        except:
            user = message.server.get_member(user_id)
            betting.add_account(user_id, user.name, 0)
            betting.transaction(SHINOBU_PROTOCREDIT_RESERVE, user_id, 10, "Enroll bonus")
            user_record = Account(user_id)
        await shinobu.send_message(message.channel, "<@{}> has {} protocredits.".format(user_id, round(user_record["Balance"], 2)))

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
                await shinobu.send_message(message.channel, "Valid games are {}".format(games))
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
    async def credit(message: discord.Message, arguments: str):
        args = arguments.rsplit()
        try:
            num = float(args[0])
            user = message.mentions[0]
            betting.transaction(message.author, user, num)
            await shinobu.send_message(message.channel, "Credited <@{}> {} protocredits.".format(user.id, num))
        except:
            pass




