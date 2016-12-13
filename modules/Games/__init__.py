from importlib import reload as reloadmod
import Games.simple_games as simple_games
simple_games = reloadmod(simple_games)
import Games.betting as betting
betting = reloadmod(betting)
import discord
from Shinobu.client import Shinobu
import asyncio
from math import floor
from random import randint







version = "1.0.0"



async def accept_message(message:discord.Message):
    chance, new = betting.get_user_balance(message.author.id)
    chance = floor(chance + 1)**2
    num = randint(0,chance)
    if num == 0:
        await shinobu.send_message(message.channel, "Congrats! You've earned a protocredit.")
        betting.credit_user(message.author, 1)

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

shinobu = None # type: Shinobu

games = {
    "roll":simple_games.roll_dice,
    "flip":simple_games.flip
}


def register_commands(ShinobuCommand):
    @ShinobuCommand("Rolls n dice. By default, five.", ["all"])
    async def roll(message: discord.Message, arguments: str):
        try:
            num_dice = int(arguments)
        except:
            num_dice = 5
        text, odds = simple_games.roll_dice(num_dice)
        await shinobu.send_message(message.channel, text)

    @ShinobuCommand("Flips a coin", ["all"])
    async def flip(message: discord.Message, arguments: str):
        mes = await shinobu.send_message(message.channel, "Flipping a coin for {}.\n".format(arguments))
        await shinobu.send_typing(message.channel)
        text = ["Heads!", "Tails!"]
        f = randint(0, 1)
        await asyncio.sleep(1)
        await shinobu.send_message(message.channel, text[f])

    @ShinobuCommand("Lists the balances of everyone")
    async def top(message: discord.Message, arguments: str):
        limit = 10
        output = "Top 10 Balances:\n```"
        for account in sorted(betting.get_all_accounts(), key=lambda x:x['balance'], reverse=True):
            member = message.server.get_member(account['id'])
            output+= "{:20} Balance: [{}]\n".format(member.name, round(account['balance'], 2))

        await shinobu.send_message(message.channel, output + "```")

    @ShinobuCommand("Lists purchaseable items", ['all'])
    async def store(message: discord.Message, arguments: str):
        output = "Items available:\n"
        for item in sorted(betting.config['store_items'], key=lambda x:x['name']):
            output+=item['name'] + " - " + item['price'] + "\n"
        await shinobu.send_message(message.channel, output)

    @ShinobuCommand("Displays user balance", ["all"])
    async def bal(message: discord.Message, arguments: str):
        if arguments is "":
            user_id = message.author.id
        else:
            user_id = message.mentions[0].id
        balance, new = betting.get_user_balance(user_id)
        if new:
            await shinobu.send_message(message.channel, "Welcome, <@{}> you've been awarded {} protocredits.".format(user_id, 10))
        await shinobu.send_message(message.channel, "<@{}> has {} protocredits.".format(user_id, round(balance, 2)))

    @ShinobuCommand(".bet amount game", ["all"])
    async def bet(message: discord.Message, arguments: str):
        args = arguments.rsplit()
        try:
            amount = float(args[0])
        except:
            await shinobu.send_message(message.channel, "The first argument must be the amount you want to bet.")
            return
        try:
            game = args[1]
        except:
            shinobu.send_message(message.channel, "The second argument must be a game.")
            return
        try:
            bet = betting.Bet(game, amount, message.author)
            text, odds = games[game]()
            print(odds)
            await shinobu.send_message(message.channel, text)

            won = True if odds >= 0 else False
            amount = bet.conclude_bet(won, odds)
            result_text = "won" if won else "lost"
            output = "<@{}> {} **{}** protocredits.".format(message.author.id, result_text, round(amount, 2))
        except Exception as e:
            print(e)
            output = "You don't have enough protocredits to bet."
        await shinobu.send_message(message.channel, output)

    @ShinobuCommand("Rolls n dice. By default, five.", ["owner"])
    async def credit(message: discord.Message, arguments: str):
        args = arguments.rsplit()
        try:
            num = float(args[1])
            user = message.mentions[0]
            betting.credit_user(user, num)
            await shinobu.send_message(message.channel, "Credited <@{}> {} protocredits.".format(user.id, num))
        except:
            pass




