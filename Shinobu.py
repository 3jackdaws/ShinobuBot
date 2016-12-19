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
        for module in shinobu.get_modules():
            try:
                if hasattr(module, "accept_message"):
                    await module.accept_message(message)
            except StopPropagationException as e:
                raise e
            except Exception as e:
                await shinobu.send_message(shinobu.get_channel(shinobu.owner), "There seems to be a problem with the {0} module".format(module.__name__))
                await shinobu.send_message(shinobu.get_channel(shinobu.owner),("[{0}]: " + str(e)).format(module.__name__))
                print(sys.exc_info()[0])
                print(sys.exc_traceback)

        if message.content[0] is "." or message.content[0] is "!":
            command = message.content.rsplit(" ")[0][1:]
            arguments = " ".join(message.content.rsplit(" ")[1:])
            shinobu.exec(command, message)
            if message.content[0] is "!":
                await shinobu.delete_message(message)
            return





    except StopPropagationException as e:
        print("Module", e, " has prevented message propagation")



if len(shinobu.login_token) > 20:
    print(shinobu.login_token)
    shinobu.run(shinobu.login_token)
elif "@" in shinobu.login_email:
    shinobu.run(shinobu.login_email,shinobu.login_password)
else:
    print("An email and password, or a login token must be set in the config")