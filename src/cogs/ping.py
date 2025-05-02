from datetime import datetime
import math
import discord
from discord import app_commands
from discord.ext import commands


class PingCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(__name__)

    @app_commands.command(description="botの応答速度を計測")
    async def ping(self, interaction: discord.Interaction) -> None:
        pong = "Ping値計測中...⌚"
        start_time = datetime.now()
        await interaction.response.send_message(pong, ephemeral=True)

        elapsed_time = (
            f"Pong!🏓 {math.floor((datetime.now() - start_time).microseconds/1000)} ms"
        )
        await interaction.edit_original_response(content=elapsed_time)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PingCog(bot))
