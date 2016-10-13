import discord
import threading
import asyncio


def write_config():
    global channels
    import json
    cfile = open("resources/reminder_list.json", "w")
    json.dump(channels, cfile)

def load_config():
    global channels

def send_message(message):
    channel = shinobu.get_channel(232224215175004160)
    asyncio.ensure_future(shinobu.send_message(channel, message))

def accept_shinobu_instance(i: discord.Client):
    global shinobu, server_thread
    shinobu = i
    for module in shinobu.loaded_modules:
        if hasattr(module, "endpoint"):
            print("Register gh endpoint")
            @module.endpoint.route("/github", methods=['POST', 'GET'])
            def github_post():
                import json
                print("Github endpoint accessed")
                data = module.request.get_json()
                action = data["action"]
                if action in ["assigned", "unassigned", "labeled", "unlabeled", "opened", "edited", "closed", "reopened"]:
                    sender = data["sender"]["login"]
                    org = data["organization"]["login"]
                    repofull = data["pull_request"]["head"]["repo"]["full_name"]
                    message = "{0} has {1} a pull request in {2}".format(sender, action, repofull)
                    send_message(message)
                return "Shinobu Github Endpoint"
            return
    raise ImportWarning("ShinobuEndpointService must be present for the GithubNotifications module to function")

version = "0.0.2"
shinobu = None # type: discord.Client
channels = []



def register_commands(ShinobuCommand):
    @ShinobuCommand("Register a Pull Request notifier")
    async def addpullrec(message: discord.Message, arguments: str):
        pass




