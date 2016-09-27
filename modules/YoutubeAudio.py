import discord
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
                if not discord.opus.is_loaded():
                    discord.opus.load_opus("libopus0")
                shinobuplayer = await shinobu.join_voice_channel(vchannel)
                youtubeplayer = await shinobuplayer.create_ytdl_player(arguments, use_avconv=True)
                youtubeplayer.start()

