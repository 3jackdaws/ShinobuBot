from flask import Flask, request
from threading import Thread
import urllib.request
import discord

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

def cleanup():
    global endpoint, endpoint_thread
    stop_endpoint()
    endpoint_thread.join()


def register_commands(ShinobuCommand):
    @ShinobuCommand("List registered endpoints")
    async def endpoints(message: discord.Message, arguments: str):
        global endpoint #type: Flask
        output = "__**Routes**__\n"
        for rule in endpoint.url_map.iter_rules():
            output += rule.__str__() + "\n"
        await shinobu.send_message(message.channel, output)


def start_endpoint():
    global endpoint
    print("Starting Shinobu Endpoint Service")
    endpoint.run("0.0.0.0", 5000)

def stop_endpoint():
    global endpoint, endpoint_thread
    print("Stopping Shinobu Endpoint Service")
    # lol, this is the dumbest thing I've ever seen
    try:
        urllib.request.urlopen("http://localhost:5000/stop")
    except:
        pass
    endpoint_thread.join()

version = "0.2.4"
shinobu = None # type: discord.Client
endpoint = Flask(__name__) # type: Flask
@endpoint.route("/stop")
def shutdown():
    stop = request.environ.get('werkzeug.server.shutdown')
    if stop is None:
        raise RuntimeError('The Endpoint service cannot be stopped, we lost the thread.  The robot uprising has begun.')
    stop()
    return "Stopping endpoint"
@endpoint.route("/test")
def test():
    return "Test"
endpoint_thread = Thread(target=start_endpoint)
endpoint_thread.start()


