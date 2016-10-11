import discord
import re
import subprocess

import select
import socket
import struct

"""
Minecraft RCON Client API

Based on implementation details from http://wiki.vg/Rcon
"""


class MessageTypes(object):
    """ Message types used by the RCON API. Only used when sending data at the
    moment, but could be used to verify the types of incoming data.
    """
    RCON_AUTHENTICATE = 3
    RCON_AUTH_RESPONSE = 2
    RCON_EXEC_COMMAND = 2
    RCON_EXEC_RESPONSE = 0


class ConnectionError(Exception):
    """ Occurs when the client socket fails to connect to the listening RCON
    server.
    """
    pass


class AuthenticationError(Exception):
    """ Occurs when the wrong password is provided to an RCON server.
    """
    pass


class RemoteConsole(object):
    """ The core piece of api.rcon. Connects to a requested server and
    authenticates, then allows commands to be sent with send(). Can also close
    its client socket with disconnect().
    """

    def __init__(self, host, port, password):
        """ Sets up our RemoteConsole, creates the socket, connects to the
        RCON API, and authenticates.

        @param host: Address of the Minecraft server (default: 127.0.0.1)
        @param port: Port RCON is running on (default: 25575)
        @param password: RCON password for the server (required)
        """
        self.host = host
        self.port = port
        self.password = password

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(1.0)
        try:
            self.client.connect((self.host, self.port))
        except:
            raise ConnectionError

        if not self.authenticate():
            raise AuthenticationError

    def send(self, command, authenticate=False):
        """ Creates a packed header struct based on the command parameters,
        and sends the combined header, command, and null byte padding to the
        RCON server.

        Header Struct (little-endian):
            Padded command length (int)
            Message ID (int)
            Message type (int)

        Reads the header from the client socket, then streams data until
        no data is left to be read from the socket. We read 12 bytes at a time
        to receive three 4-byte integers.

        The read loop uses select() to check the client socket for remaining
        data. The client socket is passed in for a readability check, and the
        returned list indicates whether or not data remains to be read. When
        the returned list is empty, the loop ends.

        In this loop, we read from the socket until all data has been received,
        then combine the response and return it along with the response ID,
        which allows us to verify authentication attempts.

        @param command: RCON command to send to the server (e.g. "say hi")
        @param authenticate: Set to True to use the auth message type
        @return: response text (str), message ID (int)
        """
        response = b''
        data_remains = True

        # send the command
        header = struct.pack(
            "<iii",
            len(command) + 10,
            0,
            MessageTypes.RCON_AUTHENTICATE if authenticate is True
            else MessageTypes.RCON_EXEC_COMMAND
        )
        self.client.send(header + command.encode('utf-8') + b"\x00\x00")

        # return the response
        response_length, response_id, response_type = struct.unpack(
            "<iii",
            self.client.recv(12)
        )
        while data_remains:
            response_fragment = self.client.recv(response_length - 8)
            response += response_fragment.strip(b"\x00\x00")
            data_remains = select.select([self.client], [], [], 1.0)[0]
        return response, response_id

    def authenticate(self):
        """ Sends an authentication packet to the RCON server and checks the
        response for a matching message ID. A message ID of -1 indicates
        authentication failure, and a matching message ID (0 in our case)
        indicates success.

        @return: True or False based on authentication success/failure
        """
        response, response_id = self.send(self.password, authenticate=True)
        return response_id == 0

    def disconnect(self):
        """ Close the client socket if connected to the RCON server.
        """
        self.client.close()

async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu, operators
    shinobu = instance
    try:
        operators = shinobu.config['minecraft_operators']
    except:
        operators = []


operators = []
version = "1.0.0"
shinobu = None
rcon = None
try:
    rcon = RemoteConsole(host='isogen.net', port=3333, password='rconpasstest1')
except:
    pass

def say_as_shinobu(message):
    response = rcon.send("tellraw @a {text:\"[Shinobu] " + message + "\", color:green}")

def register_commands(ShinobuCommand):
    @ShinobuCommand("Runs a command and returns the output -- Owner only")
    async def run(message:discord.Message, arguments:str):
        if shinobu.author_is_owner(message):
            response = rcon.send(arguments)
            response = response[0].decode()
            if arguments.startswith("help"):
                response = re.sub(r"([^(])/",r"\1\n/",response)
            await shinobu.send_message(message.channel, response)

    @ShinobuCommand("Starts the minecraft server")
    async def start(message: discord.Message, arguments: str):
        if shinobu.author_is_owner(message) or message.author in operators:
            if rcon is None:
                result = subprocess.check_output(["sh", "/home/shinobu/infinity/ServerStart.sh"]).decode()
            else:
                result = "The server might already be running.  Try reloading the module."
            await shinobu.send_message(message.channel, result)

    @ShinobuCommand("Tell message to entire server")
    async def say(message: discord.Message, arguments: str):
        if shinobu.author_is_owner(message) or message.author in operators:
            say_as_shinobu(arguments)

    ["kick", "morpheus", "setworldspawn", "tell", "warp", "op", "deop"]