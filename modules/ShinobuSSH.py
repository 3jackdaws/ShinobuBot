import discord
from subprocess import check_output

async def accept_message(message:discord.Message):
    if message.content[0] is "~":
        command = message.content.rsplit(" ")[0][1:]
        arguments = " ".join(message.content.rsplit(" ")[1:])
        # print("COMMAND: {0}, ARGUMENTS: {1}".format(command, arguments))
        if command in SSHCommandList:
            await SSHCommandList[command](message, arguments)



def accept_shinobu_instance(i:discord.Client):
    global shinobu
    shinobu = i

def load_config():
    import json
    global ssh_pass, ssh_user
    infile = open('shinobu_config.json', 'r')
    config = json.load(infile)
    ssh_user = config["ssh"]["user"]
    ssh_pass = config["ssh"]["password"]
    ssh_host = config["ssh"]["host"]
    # print(ssh_user, ssh_pass)

def ShinobuSSHCommand(description):
    global SSHCommandList
    global SSHCommandDesc
    def find_command(command_function):
        SSHCommandList[command_function.__name__] = command_function
        SSHCommandDesc[command_function.__name__] = description
        return command_function
    return find_command

version = "1.0.2"
shinobu = None
ssh_user = None
ssh_pass = None
ssh_host = None
SSHCommandList = {}
SSHCommandDesc = {}
load_config()

@ShinobuSSHCommand("")
def say(message:discord.Message, arguments:str):
    result = check_output(["ssh", ssh_user+"@"+ssh_host])