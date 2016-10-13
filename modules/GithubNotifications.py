import discord
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class PostRequestResponder(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")
        print(post_data)

def accept_shinobu_instance(i: discord.Client):
    global shinobu
    shinobu = i
    server_thread.run()

def cleanup():
    server.shutdown()
    server_thread.join()

def run_server():
    global server
    print("Starting HTTP server")
    address = ('127.0.0.1', 5000)
    server = HTTPServer(address, PostRequestResponder)
    server.serve_forever()

version = "1.0.0"
shinobu = None # type: discord.Client
server_thread = threading.Thread(args=run_server)
server = None #type: HTTPServer


def register_commands(ShinobuCommand):
    @ShinobuCommand("Register a Pull Request notifier")
    async def addpullrec(message: discord.Message, arguments: str):
        pass




