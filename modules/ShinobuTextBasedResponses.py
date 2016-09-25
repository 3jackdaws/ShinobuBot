import re

import discord

import resources
from modules import ShinobuCommands

shinobu = ShinobuCommands.get_instance()

nice_memes = ["4 u",
              "for you",
              "for u",
              "4 you",
              "ur dumb",
              "gabe",
              "bork",
              "autism"]

thanks = ["nice meme"]

def BanePost4U(func):
    def fy_responder(message:discord.Message):
        if re.search("big guy",message.content.lower()) is not None:
            return "for you"
        return func(message)
    return fy_responder

def BanePostBigGuy(func):
    def bg_responder(message:discord.Message):
        if re.search("(^|[^a-z])bane($|[^a-z])",message.content.lower()) is not None:
            return "he's a big guy"
        return func(message)
    return bg_responder

def NiceMemer(func):
    def nm_responder(message:discord.Message):
        for meme in nice_memes:
            regexp = "(^|[^a-z])" + meme + "($|[^a-z])"
            if re.search(regexp,message.content.lower()) is not None:
                return "nice meme"
        return func(message)
    return nm_responder

def Thanks(func):
    def thnx_responder(message:discord.Message):
        for meme in thanks:
            regexp = "(^|[^a-z])" + meme + "($|[^a-z])"
            if re.search(regexp,message.content.lower()) is not None:
                return "thnx :^)"
        return func(message)
    return thnx_responder

def PairedResponse(func):
    def pair_responder(message:discord.Message):
        for key in resources.pair_response:
            if resources.pair_response.get(key) is None:
                continue
            regexp = "(^|[^a-z])" + key + "($|[^a-z])"
            if re.search(regexp,message.content.lower()) is not None:
                response = resources.pair_response.get(key)
                if isinstance(response, list):
                    response = resources.choose_random(response)
                return response
        return func(message)
    return pair_responder

@ShinobuTextBasedResponses.PairedResponse
def text_based_response(message:discord.Message):
    return None