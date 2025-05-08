import discord
from discord import app_commands
from discord.ext import commands


class ConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(__name__)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ConfigCog(bot))
