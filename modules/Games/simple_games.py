import discord
from classes.Shinobu import Shinobu
from random import randint
import asyncio



lookup = {
        1: ":one:",
        2: ":two:",
        3: ":three:",
        4: ":four:",
        5: ":five:",
        6: ":six:"
    }

dice_odds = {

}

def flip():
    ht = ["Heads!","Tails!"]
    val = randint(0,1)
    if val == 0:
        odds = 1
    else:
        odds = -1
    return ht[val], odds

def roll_dice(num_dice = 5):
    total = 0
    odds = -1
    results = "**Total**: {}/{} [{}%]\n"
    if num_dice > 100 or num_dice < 1:
        return "You can only roll between 1 and 100 dice."
    count_dice = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
    }
    for i in range(0, num_dice):
        res = randint(1, 6)
        count_dice[res] += 1
        total += res
        results += lookup[res] + " "
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
    percent = round((total / (max)) * 100)
    results = results.format(total, max, percent)
    if percent > 80:
        results += "\nExceptional Roll!"
    elif percent > 69:
        results += "\nGood Roll!"
    odds = ((percent - 51.5)/100) * max_num
    print("ODDS:", odds)
    return results, odds

