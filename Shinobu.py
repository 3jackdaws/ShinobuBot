from classes.Shinobu import Shinobu
import discord
import sys

shinobu = Shinobu("resources/")



shinobu.reload_config()
shinobu.load_all()

@shinobu.event
async def on_ready():
    print('Logged in as:', shinobu.user.name)
    print('-------------------------')
    # print(loaded_modules)


@shinobu.event
async def on_message(message:discord.Message):

        if message.author.id == shinobu.user.id: return;

        if message.content[0] == "!" and shinobu.author_is_owner(message):
            if message.content.rsplit(" ")[0] == "!safemode":
                await shinobu.send_message(message.channel, "Loading safemode modules")
                shinobu.safemode()
            elif message.content.rsplit(" ")[0] == "!pause":
                if shinobu.idle:
                    shinobu.idle = False
                    await shinobu.change_presence(status=discord.Status.online)
                    await shinobu.send_message(message.channel, "ShinobuBot on {0} checking in".format(shinobu.config["instance name"]))
                    print("UNPAUSED")
                else:
                    shinobu.idle = True
                    await shinobu.change_presence(status=discord.Status.idle)
                    await shinobu.send_message(message.channel, "Paused")
                    print("PAUSED")

        if shinobu.idle == True: return
        if message.content[0] is ".":
            command = message.content.rsplit(" ")[0][1:]
            arguments = " ".join(message.content.rsplit(" ")[1:])
            if command in shinobu.command_list:
                await shinobu.command_list[command](message, arguments)

        for module in shinobu.loaded_modules:
            try:
                if hasattr(module, "accept_message"):
                    await module.accept_message(message)
            except Exception as e:
                await shinobu.send_message(shinobu.config["owner"], "There seems to be a problem with the {0} module".format(module.__name__))
                await shinobu.send_message(shinobu.config["owner"],("[{0}]: " + str(e)).format(module.__name__))
                print(sys.exc_info()[0])
                print(sys.exc_traceback)


shinobu.run('MjI3NzEwMjQ2MzM0NzU4OTEz.CsKHOA.-VMTRbjonKthatdxSldkcByan8M')