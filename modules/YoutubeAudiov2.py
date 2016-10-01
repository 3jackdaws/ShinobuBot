import discord
import nacl
import discord.opus
import youtube_dl
import asyncio
import re


class ShinobuAudioStream:
    def __init__(self, title=None, length=None, file=None):
        self.stitle = title
        self.slength = length
        self.file = file # type: str
        self.stream = open(self.file, "rb")

    def read(self, n=-1):
        return self.stream.read(n)

    @property
    def title(self):
        return self.stitle

    @property
    def length(self):
        return self.slength

class ShinobuStreamPlayer:
    def __init__(self, client:discord.Client):
        self.client = client # type: discord.Client
        self.channel = None
        self.voice_client = None # type: discord.VoiceClient
        self.stream_player = None
        self.audio_queue = [] # type: [ShinobuAudioStream]
        self.current = None


    def leave_channel(self):
        if self.in_channel():
            self.voice_client.disconnect()
            self.voice_client = None
            self.channel = None

    def end_player_thread(self):
        if self.stream_player is not None and self.stream_player.is_alive:
            self.stream_player.stop()
            self.stream_player.join()

    def author_voice_channel(author: discord.Member):
        for channel in shinobu.get_all_channels():
            if author in channel.voice_members:
                return channel
        return None

    def notify(self):
        if self.current is None and len(self.audio_queue) > 0:
            next = self.audio_queue.pop()

            self.current = self.voice_client.create_ffmpeg_player(next, after=self.notify(), use_avconv=True)
            self.current.start()

    def queue_audio_stream(self, shinobu_stream:ShinobuAudioStream):
        self.audio_queue.append(shinobu_stream)

    async def enter_channel(self, channel:discord.Channel):
        print(channel.type)
        if channel.type is discord.enums.ChannelType.voice:
            if self.channel == channel:
                return
            if self.voice_client is not None and self.voice_client.is_connected():
                await self.voice_client.disconnect()
            self.channel = channel
            self.voice_client = await self.client.join_voice_channel(channel)
            self.end_player_thread()
        else:
            raise discord.DiscordException(Exception("Channel is not a voice channel"))

    def in_channel(self, channel:discord.Channel = None):
        if channel is None and self.channel is not None:
            return True
        elif self.channel == channel:
            return True
        return False

version = "0.0.3"

async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance
    global stream_player
    stream_player = ShinobuStreamPlayer(shinobu)

shinobu = None # type: discord.Client
stream_player = None # type: ShinobuStreamPlayer

def register_commands(ShinobuCommand):
    @ShinobuCommand("Tells Shinobu to queue a Youtube video")
    async def yt(message: discord.Message, arguments: str):
        global stream_player # type: ShinobuStreamPlayer
        channel = ShinobuStreamPlayer.author_voice_channel(message.author)
        print("Channel", channel)
        if channel is None:
            await shinobu.send_message(message.channel, "You must be in a voice channel to use that command.")
        elif not stream_player.in_channel(channel):
            print("Not in channel")
            await stream_player.enter_channel(channel)
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(arguments)
            filename = ydl.prepare_filename(info_dict)
            print("Filename:",filename)
            title = info_dict.get("title")
            length = info_dict.get("duration")

        filename = re.sub("[a-z]+?$", "opus", filename)
        print(filename)
        # stream = open(filename, "rb")
        stream_player.queue_audio_stream(filename)
        stream_player.notify()




