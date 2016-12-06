from classes.Shinobu import Shinobu, StopPropagationException
import discord
import sys

shinobu = Shinobu("resources/")


@shinobu.event
async def on_ready():
    print('Logged in as:', shinobu.user.name)
    print('-------------------------')
    shinobu.reload_config()
    shinobu.load_all()


@shinobu.event
async def on_message(message:discord.Message):
    try:

        if message.content[0] == "!":
            if shinobu.author_is_owner(message):
                if message.content.rsplit(" ")[0] == "!safemode":
                    await shinobu.send_message(message.channel, "Loading safemode modules")
                    shinobu.safemode()
                elif message.content.rsplit(" ")[0] == "!pause":
                    if shinobu.idle:
                        shinobu.idle = False
                        await shinobu.change_presence(status=discord.Status.online)
                        await shinobu.send_message(message.channel, "*Tuturu!*\nShinobu desu, [{0}]".format(shinobu.config["instance name"]))
                        print("UNPAUSED")
                    else:
                        shinobu.idle = True
                        await shinobu.change_presence(status=discord.Status.idle)
                        await shinobu.send_message(message.channel, "Paused")
                        print("PAUSED")
            elif message.author.id == shinobu.user.id:
                command = message.content.rsplit(" ")[0][1:]
                arguments = " ".join(message.content.rsplit(" ")[1:])
                shinobu.exec(command, message)
                if arguments == "rm":
                    await shinobu.delete_message(message)

        if shinobu.idle: return
        if message.author.id == shinobu.user.id: return;

        for module in shinobu.loaded_modules:
            try:
                if hasattr(module, "accept_message"):
                    await module.accept_message(message)
            except StopPropagationException as e:
                raise e
            except Exception as e:
                await shinobu.send_message(shinobu.get_channel(shinobu.config["owner"]), "There seems to be a problem with the {0} module".format(module.__name__))
                await shinobu.send_message(shinobu.get_channel(shinobu.config["owner"]),("[{0}]: " + str(e)).format(module.__name__))
                print(sys.exc_info()[0])
                print(sys.exc_traceback)

        if message.content[0] is ".":
            command = message.content.rsplit(" ")[0][1:]
            arguments = " ".join(message.content.rsplit(" ")[1:])
            shinobu.exec(command, message)

    except StopPropagationException as e:
        print("Module", e, " has prevented message propagation")


shinobu.run('MjI3NzEwMjQ2MzM0NzU4OTEz.CsKHOA.-VMTRbjonKthatdxSldkcByan8M')