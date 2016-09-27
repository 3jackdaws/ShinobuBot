import discord
import pafy
import nacl
import discord.opus



version = "0.0.2"

async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu
    shinobu = instance

shinobu = None

def register_commands(ShinobuCommand):
    @ShinobuCommand("Tells Shinobu to queue a Youtube video")
    async def yt(message:discord.Message, arguments:str):
        print(arguments)
        for vchannel in shinobu.get_all_channels():
            if message.author in vchannel.voice_members:
                video = pafy.new(arguments)
                audiostream = video.getbestaudio()
                filename = audiostream.download(quiet=True)
                file = open(filename, "rb")
                if not discord.opus.is_loaded():
                    discord.opus.load_opus("opusdec")
                shinobuplayer = await shinobu.join_voice_channel(vchannel)
                await shinobuplayer.create_stream_player(file)

