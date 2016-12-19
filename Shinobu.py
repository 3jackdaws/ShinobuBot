from Shinobu.client import Shinobu, StopPropagationException
import discord
import sys

shinobu = Shinobu("resources/")


@shinobu.event
async def on_ready():
    shinobu.log("SHINOBU", 'Logged in as: {}'.format(shinobu.user.name))
    print('-------------------------')
    shinobu.load_all()


@shinobu.event
async def on_channel_delete(channel:discord.Channel):
    try:
        for module in shinobu.get_modules():
            try:
                if hasattr(module, "on_channel_delete"):
                    await module.on_channel_delete(channel)
            except StopPropagationException as e:
                raise e
            except Exception as e:
                await shinobu.send_message(shinobu.get_channel(shinobu.owner), "There seems to be a problem with the {0} module".format(module.__name__))
                await shinobu.send_message(shinobu.get_channel(shinobu.owner),("[{0}]: " + str(e)).format(module.__name__))
                print(sys.exc_info()[0])
                print(sys.exc_traceback)
    except StopPropagationException as e:
        shinobu.log(e, "Prevent chan del Propagation")


@shinobu.event
async def on_message(message:discord.Message):
    try:
        for module in shinobu.get_modules():
            try:
                if hasattr(module, "on_message"):
                    await module.on_message(message)
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
        shinobu.log(e, "Prevent Message Propagation")



if len(shinobu.login_token) > 20:
    shinobu.run(shinobu.login_token)
elif "@" in shinobu.login_email:
    shinobu.run(shinobu.login_email,shinobu.login_password)
else:
    print("An email and password, or a login token must be set in the config")