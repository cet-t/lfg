import asyncio
from dis import disco
import math
import discord
from discord import app_commands
from discord.ext import commands

from utils.nullable import nullable
from utils.util import datetime_format, dpy_util, mention_type


class PingCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.bot.tree.sync()
        print(__name__)

    @commands.hybrid_command()
    async def ping(self, ctx: commands.Context) -> None:
        pong = f"Pong! {math.floor(self.bot.latency * 1000)} ms"
        if ctx.interaction is None:
            await ctx.reply(pong, ephemeral=True)
        else:
            await ctx.interaction.response.send_message(pong, ephemeral=True)

    @commands.hybrid_command(name="info")
    async def info(self, ctx: commands.Context) -> None:
        author = ctx.author if ctx.interaction is None else ctx.interaction.user
        embed = discord.Embed(title=f"{author.global_name} ({author.display_name})")
        if ctx.guild is not None:
            member = await ctx.guild.fetch_member(author.id)

            dpy_util.add_code_field(
                embed,
                "アカウント作成日時",
                author.created_at.__format__(datetime_format.yyyymmddhhmmss),
                False,
            )
            dpy_util.add_code_field(
                embed,
                "サーバー参加日時",
                member.joined_at.__format__(datetime_format.yyyymmddhhmmss),
                False,
            )
            dpy_util.add_code_field(
                embed,
                "ロール",
                str.join("\n", [f"- {role.name}" for role in member.roles]),
                False,
            )
        if ctx.interaction is None:
            await ctx.send(embed=embed, ephemeral=True)
            await ctx.message.delete()
        else:
            await ctx.interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PingCog(bot))
