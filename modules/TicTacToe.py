import discord
from random import random
import math
async def accept_message(message:discord.Message):
    if message.content[0] == "/":
        if "/ttt" == message.content[:4]:
            arguments = message.content[5:]
            print(arguments)
            if arguments.rsplit(" ")[0].isdigit():
                await commands["place"](message, arguments)
            else:
                await commands[arguments.rsplit(" ")[0]](message,arguments)




def accept_shinobu_instance(i:discord.Client):
    global shinobu
    shinobu = i


version = "1.0.3"
shinobu = None

gameboards = {}


emojo_lookup = {1:":one:",
                2:":two:",
                3:":three:",
                4:":four:",
                5:":five:",
                6:":six:",
                7:":seven:",
                8:":eight:",
                9:":nine:",
                'X':":doughnut:",
                'O':":sun_with_face:"}

async def help(message:discord.Message, arguments:str):
    helpstring = "Shinobu Tic Tac Toe Module Help\n" \
                 "COMMANDS:\n" \
                 "**play**   Start a new game\n" \
                 "**view**   View a current game\n" \
                 "**[1-9]**  Place a game piece\n"

    await shinobu.send_message(message.channel, helpstring)

async def play(message:discord.Message, arguments:str):
    author = message.author.id
    gameboards[author] = {"board":[1,2,3,4,5,6,7,8,9],
                          "last message":None}
    user_go_first = math.floor(random()*2) == 0
    turn_msg = "You go first!"
    if not user_go_first:
        gameboards[author]["board"][math.floor(random()*9)] = "X"
        turn_msg = "Your turn!"
    await shinobu.send_message(message.channel, drawboard(gameboards[author]["board"]))
    await shinobu.send_message(message.channel, turn_msg)

def drawboard(board:list):
    output = ""
    index = 0
    for cell in board:
        output+= emojo_lookup[cell]
        index+=1
        if index % 3 == 0:
            output+= "\n"
    return output

async def place(message:discord.Message, arguments:str):
    author = message.author.id
    if gameboards.get(author) is None or not isinstance(gameboards[author]["board"], list):
        await shinobu.send_message(message.channel, "You need to start a game first.  Use /ttt play to do that.")
        return
    index = int(arguments)-1
    cell_is = gameboards[author]["board"][index]
    if index < 0 or index > 8 or cell_is == "X" or cell_is == "O":
        await shinobu.send_message(message.channel, "You can't go there :(")
    else:
        gameboards[author]["board"][index] = "O"
        winner = has_won(gameboards[author]["board"])
        if winner is not False:
            await shinobu.send_message(message.channel, drawboard(gameboards[author]["board"]))
            if winner == "X":
                await shinobu.send_message(message.channel, "I won!")
            else:
                await shinobu.send_message(message.channel, "Wow, you won!")
            gameboards[author]["board"] = None
            return
        place_location = math.floor(random()*9)
        placed = False
        while not placed:
            cell_fill = gameboards[author]["board"][place_location]
            if cell_fill == "X" or cell_fill == "O":
                place_location = math.floor(random() * 9)
            else:
                gameboards[author]["board"][place_location] = "X"
                placed = True
        winner = has_won(gameboards[author]["board"])

        if winner is not False:
            await shinobu.send_message(message.channel, drawboard(gameboards[author]["board"]))
            if winner == "X":
                await shinobu.send_message(message.channel, "I won!")
            else:
                await shinobu.send_message(message.channel, "Wow, you won!")

            gameboards[author]["board"] = None
            return
        await shinobu.send_message(message.channel, drawboard(gameboards[author]["board"]))



def has_won(board:list):
    def check_col(board:list, col:int):
        token = board[col]
        for cel in [col, col+3, col+6]:
            if not board[cel] == token:
                return False
        return token
    def check_row(board:list, row:int):
        row = row*3
        token = board[row]
        for cel in [row, row+1, row+2]:
            if not board[cel] == token:
                return False
        return token
    def check_cross(board:list, start):
        increment = 4 - start
        token = board[start]
        for cel in [start, start+increment, start+increment+increment]:
            if not board[cel] == token:
                return False
        return token
    for col in [0,1,2]:
        winner = check_col(board, col)
        if winner is not False:
            return winner

    for row in [0,1,2]:
        winner = check_row(board, row)
        if winner is not False:
            return winner

    for start in [0,2]:
        winner = check_cross(board, start)
        if winner is not False:
            return winner
    return False


commands = {"help":help,
            "play":play,
            "place":place}