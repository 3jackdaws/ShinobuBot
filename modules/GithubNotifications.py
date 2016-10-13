import discord
import threading
import asyncio

def send_message():
    pass

def write_reminder():
    global reminder_list
    import json
    reminder_file = open("resources/reminder_list.json", "w")
    json.dump(reminder_list, reminder_file)

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
                for key in data:
                    print(key)
                print(data["sender"]["login"])
                print(data["organization"]["login"])
                return "Shinobu Github Endpoint"
            return
    raise ImportWarning("ShinobuEndpointService must be present for the GithubNotifications module to function")

version = "0.0.2"
shinobu = None # type: discord.Client



def register_commands(ShinobuCommand):
    @ShinobuCommand("Register a Pull Request notifier")
    async def addpullrec(message: discord.Message, arguments: str):
        pass




