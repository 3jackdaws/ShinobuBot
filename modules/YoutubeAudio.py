import discord
import nacl
import discord.opus
import pafy
import asyncio



version = "0.0.3"

async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

def cleanup():
    global music
    global voice
    print("Module YoutubeAudio cleaning up")
    if music['current'] is not None:
        music['current'].stop()
    if voice is not None:
        print("Disconnect voice")
        asyncio.ensure_future(voice.disconnect())



shinobu = None # type: discord.Client

music = {}
music['queue'] = []
music['current'] = None
music['next'] = None
music['messagelist'] = []
voice = None # type:discord.VoiceClient

def get_author_voice_channel(author:discord.Member):
    for channel in shinobu.get_all_channels():
        if author in channel.voice_members:
            return channel
    return None

def assure_opus():
    if not discord.opus.is_loaded():
        discord.opus.load_opus("libopus0")

async def shinobu_connect_to(voice_channel:discord.Channel):
    global voice # type: discord.VoiceClient

    if voice is None:
        voice=await shinobu.join_voice_channel(voice_channel)
    if voice.channel == voice_channel:
        pass
    else:
        await voice.disconnect()
        voice = await shinobu.join_voice_channel(voice_channel)


def notify_track_scheduler():
    async def advance_queue():
        global music
        global voice
        if music['current'] is None or music['current'].is_done():
            if len(music['queue']) > 0:
                nexturl = music['queue'].pop()
                buffering = await shinobu.send_message(music['text-channel'], "**Buffering**:")
                music['current'] = await voice.create_ytdl_player(nexturl, use_avconv=True, after=notify_track_scheduler)
                await shinobu.edit_message( buffering, "**Now playing**:\n" + music['current'].title)
                music['current'].start()
    fut = asyncio.ensure_future(advance_queue())


def register_commands(ShinobuCommand):
    @ShinobuCommand("Tells Shinobu to queue a Youtube video")
    async def yt(message:discord.Message, arguments:str):
        print(arguments)
        global voice
        global music
        channel_called_to = get_author_voice_channel(message.author)
        if channel_called_to is None:
            await shinobu.send_message(message.channel, "You must be in a voice channel in order to use that command")
            return
        await shinobu_connect_to(channel_called_to)
        music['text-channel'] = message.channel
        video = pafy.new(arguments)
        music['messagelist'].append(await shinobu.send_message(message.channel, "**Added**:\n{0}".format(video.title)))
        music['queue'].append(arguments)
        notify_track_scheduler()


    @ShinobuCommand("Tells Shinobu to leave a channel")
    async def leave(message: discord.Message, arguments: str):
        global voice
        global music
        if arguments == "this channel":
            channel = get_author_voice_channel(message.author)
            if channel:
                music['queue'] = []
                await voice.disconnect()
                voice = None

    @ShinobuCommand("Tells Shinobu to skip to the next song")
    async def next(message: discord.Message, arguments: str):
        global music
        global voice
        if music is not None and music['current'].is_playing():
            music['current'].stop()

    @ShinobuCommand("Pauses current track")
    async def pause(message: discord.Message, arguments: str):
        global music
        if music['current'] is not None:
            if music['current'].is_playing():
                music['current'].pause()
            else:
                music['current'].resume()

    @ShinobuCommand("Lists the current queue")
    async def list(message: discord.Message, arguments: str):
        global music
        size = len(music['queue']) if len(music['queue']) < 5 else 5
        output = "**YouTube Queue**\n"
        if size == 0:
            await shinobu.send_message(message.channel, "No queued videos")
            return
        for song in music['queue']:
            video = pafy.new(song)
            output += video.title + "\n"
            size -= 1
            if size == 0:
                break
        await shinobu.send_message(message.channel, output)

