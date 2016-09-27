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
voice_client = None


def register_commands(ShinobuCommand):
    @ShinobuCommand("Tells Shinobu to queue a Youtube video")
    async def yt(message:discord.Message, arguments:str):
        print(arguments)
        global voice_client
        for vchannel in shinobu.get_all_channels():
            if message.author in vchannel.voice_members:
                if not discord.opus.is_loaded():
                    discord.opus.load_opus("libopus0")
                voice_client = await shinobu.join_voice_channel(vchannel)
                youtubeplayer = await voice_client.create_ytdl_player(arguments, use_avconv=True)
                youtubeplayer.start()

    @ShinobuCommand("Tells Shinobu to queue a Youtube video")
    async def leave(message: discord.Message, arguments: str):
        global voice_client
        if arguments == "this channel":
            channel = discord.utils.find(lambda channel: channel.voice_members == message.author, shinobu.get_all_channels())
            if channel:
                await voice_client.disconnect()
