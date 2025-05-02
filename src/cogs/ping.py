import math
import discord
from discord.ext import commands

import utils.dpy_utils


class PingCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(__name__)

    @commands.hybrid_command(description="botの応答速度を計測")
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

            utils.dpy_utils.add_code_field(
                embed,
                "アカウント作成日時",
                author.created_at.__format__(
                    utils.dpy_utils.datetime_format.yyyymmddhhmmss
                ),
                False,
            )
            utils.dpy_utils.add_code_field(
                embed,
                "サーバー参加日時",
                member.joined_at.__format__(
                    utils.dpy_utils.datetime_format.yyyymmddhhmmss
                ),
                False,
            )
            utils.dpy_utils.add_code_field(
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
