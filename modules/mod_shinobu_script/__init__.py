import discord
from Shinobu.utility import ConfigManager
from Shinobu.client import Shinobu
import re
import mod_shinobu_script.shinobu_script as ss
from mod_shinobu_script.shinobu_script import parse, get_env


async def accept_message(message:discord.Message):
    funcs = functions["on_message"].value
    for function in funcs:
        shinobu_exec(function, message, shinobu)

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

version = "1.0.1"
shinobu = None #type: Shinobu


functions = ConfigManager("resources/functions.json")
functions.assure("on_message", [])


def shinobu_exec(function, message, shinobu):
    global functions
    env = get_env(message=message, shinobu=shinobu)
    exec(functions[function].value, env)


def register_commands(ShinobuCommand):
    @ShinobuCommand("Runs shinobu script", permissions=('Shinobu Owner'))
    async def run(message: discord.Message, arguments: str):
       ss.run(message, shinobu)

    @ShinobuCommand("Compiles and stores a shinobu script routine", permissions=('Shinobu Owner'))
    async def compile(message: discord.Message, arguments: str):
        global functions
        function_name = re.findall("(?<=as )[a-zA-Z_-]+", message.content)[0]
        code = parse(message)
        functions[function_name] = code

    @ShinobuCommand("Executes a stored routine", permissions=('Shinobu Owner'))
    async def execute(message: discord.Message, arguments: str):
        shinobu_exec(arguments, message, shinobu)

    @ShinobuCommand("Binds a routine to the on_message event", permissions=('Shinobu Owner'))
    async def bind_on_message(message: discord.Message, arguments: str):
        func_name = arguments
        functions["on_message"].append(func_name)