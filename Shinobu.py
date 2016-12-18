from Shinobu.client import Shinobu, StopPropagationException
import discord
import sys

shinobu = Shinobu("resources/")


@shinobu.event
async def on_ready():
    print('Logged in as:', shinobu.user.name)
    print('-------------------------')
    shinobu.load_all()


@shinobu.event
async def on_message(message:discord.Message):
    try:
        if message.content[0] == "!" and message.author.id == shinobu.user.id:
            command = message.content.rsplit(" ")[0][1:]
            arguments = " ".join(message.content.rsplit(" ")[1:])
            shinobu.exec(command, message)
            await shinobu.delete_message(message)

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
            print(command)
            arguments = " ".join(message.content.rsplit(" ")[1:])
            shinobu.exec(command, message)
            return





    except StopPropagationException as e:
        print("Module", e, " has prevented message propagation")


email = str(shinobu.config['email'])
password = str(shinobu.config['password'])
shinobu.run(email, password)