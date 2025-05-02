import discord
from discord import app_commands
from discord.ext import commands

from uis.timemodal import TimeModal


class ConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(__name__)

    @app_commands.command(name="深夜募集時間帯変更")
    async def change_midnight(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TimeModal())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ConfigCog(bot))
