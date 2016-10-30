import discord
import nacl
import discord.opus
import youtube_dl
import asyncio
import re
from classes import Shinobu


class ShinobuAudioContainer:
    def __init__(self, title=None, length=None, stream_function=None):
        self.stitle = title
        self.slength = length
        self.stream_func = stream_function

    @property
    def streamplayer(self):
        return self.stream_func

    @property
    def title(self):
        return self.stitle

    @property
    def length(self):
        return self.slength

class ShinobuStreamPlayer:
    def __init__(self, client:Shinobu):
        self.client = client # type: discord.Client
        self.channel = None
        self.text_channel = None
        self.voice_client = None # type: discord.VoiceClient
        self.stream_player = None
        self.audio_queue = [] # type: [ShinobuAudioStream]
        self.current = None # type: discord.StreamPlayer


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

    def set_text_channel(self, channel:discord.Channel):
        if channel.type is discord.enums.ChannelType.text:
            self.text_channel = channel

    @staticmethod
    def remove_message(message:discord.Message, time:int):
        async def del_after(time):
            await asyncio.sleep(time)
            await shinobu.delete_message(message)
        asyncio.ensure_future(del_after(time))


    async def notify(self):
        if self.current is None and len(self.audio_queue) > 0:
            print("Getting next song")
            next = self.audio_queue.pop() # type: ShinobuAudioContainer
            message = await shinobu.send_message(self.text_channel, "Buffering {}".format(next.title))
            self.current = await next.streamplayer(self.voice_client)
            await shinobu.edit_message(message, "Playing {}".format(next.title))
            self.current.volume = 0.5
            self.current.start()
            self.remove_message(message, 5)
        if self.current is not None and self.current.is_done():
            print("Song Done notify next")
            self.current = None
            await self.notify()


    def queue_audio_stream(self, audio_container:ShinobuAudioContainer):
        self.audio_queue.append(audio_container)

    async def enter_channel(self, channel:discord.Channel):
        if channel.type is discord.enums.ChannelType.voice:
            if self.channel == channel:
                return
            if self.voice_client is not None and self.voice_client.is_connected():
                await self.voice_client.disconnect()
            self.channel = channel
            try:
                print("Trying to enter channel")
                self.voice_client = await self.client.join_voice_channel(channel)
            except discord.ClientException as e:
                print("Could not enter channel")
                print(e)
            self.end_player_thread()
        else:
            raise discord.DiscordException(Exception("Channel is not a voice channel"))

    def in_channel(self, channel:discord.Channel = None):
        if channel is None and self.channel is not None:
            return True
        elif self.channel == channel:
            return True
        return False

version = "0.0.4"

async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance
    global stream_player
    stream_player = ShinobuStreamPlayer(shinobu)

shinobu = None # type: discord.Client
stream_player = None # type: ShinobuStreamPlayer


def cleanup():
    print("AudioPlayer cleanup")
    server_list = []
    for channel in shinobu.get_all_channels():
        if channel.server not in server_list:
            server_list.append(channel.server)
    print(server_list)
    for server in server_list:
        if shinobu.voice_client_in(server):
            asyncio.ensure_future(shinobu.voice_client_in(server).disconnect())


def register_commands(ShinobuCommand):
    @ShinobuCommand("Lists media in the queue")
    async def list(message: discord.Message, arguments: str):
        output = "No queued audio"
        if len(stream_player.audio_queue) > 0:
            output = "**Media in queue:**\n"
            for media in stream_player.audio_queue:
                output += ("{0} - [{1}]\n".format(media.title, media.length))
        await shinobu.send_message(message.channel, output)

    @ShinobuCommand("Goes to the next song in the queue")
    async def next(message: discord.Message, arguments: str):
        if stream_player.current is not None:
            stream_player.current.stop()

    @ShinobuCommand("Tells Shinobu to queue a Youtube video")
    async def pause(message: discord.Message, arguments: str):
        if stream_player.current is not None:
            if stream_player.current.is_playing():
                stream_player.current.pause()
            else:
                stream_player.current.resume()

    @ShinobuCommand("Tells Shinobu to queue a Youtube video")
    async def yt(message: discord.Message, arguments: str):
        await shinobu.delete_message(message)
        global stream_player # type: ShinobuStreamPlayer
        channel = ShinobuStreamPlayer.author_voice_channel(message.author)
        print("Channel", channel)
        if channel is None:
            await shinobu.send_message(message.channel, "You must be in a voice channel to use that command.")
        elif not stream_player.in_channel(channel):
            print("Not in channel")
            print("Entering")
            await stream_player.enter_channel(channel)
        conf = await shinobu.send_message(message.channel, "Getting information...")
        stream_player.set_text_channel(message.channel)
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
                'preferredquality': '64',
            }],
        }
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        info_dict = ydl.extract_info(arguments, download=False)
        filename = ydl.prepare_filename(info_dict)
        title = info_dict.get("title")
        length = info_dict.get("duration")


        async def get_stream_player(voice_client:discord.VoiceClient):
            ydl.download([arguments])
            file = re.sub("[a-z]+?$", "opus", filename)
            def after():
                asyncio.ensure_future(stream_player.notify())
            return voice_client.create_ffmpeg_player(file, use_avconv=True, after=after)

        await shinobu.edit_message(conf, "**<@{0}>** added **{1}** to the queue\n({2})".format(message.author.id, title, arguments))

        stream_player.queue_audio_stream(ShinobuAudioContainer(stream_function=get_stream_player, length=length, title=title))
        await stream_player.notify()




