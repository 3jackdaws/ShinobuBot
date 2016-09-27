import discord
import nacl
import discord.opus
import pafy



version = "0.0.2"

async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

shinobu = None # type: discord.Client
voice_client = None

music = {}
music['queue'] = []
music['current'] = None
music['next'] = None
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

async def notify_track_scheduler():
    global music
    global voice
    if music['current'] is None or music['current'].is_done():
        nexturl = music['queue'].pop()
        if nexturl:
            music['current'] = await voice.create_ytdl_player(nexturl, use_avconv=True, after=notify_track_scheduler)
            music['current'].start()


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
        video = pafy.new(arguments)
        await shinobu.send_message(message.channel, "Added: {0}".format(video.title))
        music['queue'].append(arguments)
        await notify_track_scheduler()


    @ShinobuCommand("Tells Shinobu to leave a channel")
    async def leave(message: discord.Message, arguments: str):
        global voice
        if arguments == "this channel":
            channel = get_author_voice_channel(message.author)
            if channel:
                await voice.disconnect()

    @ShinobuCommand("Tells Shinobu to skip to the next song")
    async def next(message: discord.Message, arguments: str):
        global music
        global voice
        if music is not None and music['current'].is_playing():
            if len(music['queue']) > 0:
                nexturl = music['queue'].pop()
                if music['current'] is not None:
                    music['current'].stop()
                music['current'] = await voice.create_ytdl_player(nexturl, use_avconv=True, after=notify_track_scheduler)
                music['current'].start()
            else:
                music['current'].stop()
                music['current'] = None

    @ShinobuCommand("Pauses current track")
    async def pause(message: discord.Message, arguments: str):
        global music
        if music['current'] is not None:
            music['current'].pause()
