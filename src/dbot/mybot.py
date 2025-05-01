import discord


class MyBot:
    def __init__(self, bot: discord.Client):
        self.__bot = bot

    @property
    def bot(self):
        return self.__bot
