from datetime import datetime
from typing import Any, Optional
import discord
from discord import app_commands
from discord.ext import commands
import yaml

from data import LFGDict, LFGListDict
from nullable import nullable
from utils.values import params
from utils.util import (
    datetime_format,
    dpy_util,
    encoding_type,
    loading_mode,
    mention_type,
)

PATH = "./data/recruitments.yml"


class LFGEmbed(discord.Embed):
    def add_field(self, name: Any, value: Any, inline: bool = False) -> "LFGEmbed":
        return super().add_field(name=f"● {name}", value=value, inline=inline)


class LFGCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.bot.tree.sync()
        print(__name__)

    @app_commands.command()
    @app_commands.describe(
        playing="遊び方",
        vc="使用vc",
        purpose="名目",
        time="時間",
        players="人数",
        note="備考",
        thread_name="スレッド名",
    )
    async def recruit(
        self,
        interaction: discord.Interaction,
        playing: str,
        vc: discord.VoiceChannel,
        purpose: str,
        time: str,
        players: int,
        note: Optional[str] = None,
        thread_name: Optional[str] = None,
    ) -> None:
        nodes = nullable[LFGListDict](None)
        with open(PATH, loading_mode.read, encoding=encoding_type.utf8) as f:
            if (read := yaml.load(f, Loader=yaml.FullLoader)) is not None:
                nodes.value = LFGListDict(read)
        if not nodes.has_value:
            nodes.value = LFGListDict(lfgs=list[LFGDict]())

        node = LFGDict(
            recruiter_id=interaction.user.id,
            playing=playing,
            vc_id=vc.id,
            purpose=purpose,
            time=time,
            players=players,
            note=note,
        )
        nodes.value["lfgs"].append(node)
        embed = LFGCog.create_embed(node)
        await dpy_util.set_info(
            embed, interaction.guild, interaction.user, self.bot.user
        )
        response = await interaction.response.send_message(embed=embed)
        message = await interaction.channel.fetch_message(response.message_id)  # type: ignore
        thread = await message.create_thread(
            name=(
                thread_name
                if thread_name is not None
                else node.get(
                    params.lfg_dict_keys.purpose,
                    datetime.now().__format__(datetime_format.yyyymmddhhmmss),
                )
            )
        )
        thread.add_user(interaction.user)
        if thread.starter_message is not None:
            await thread.starter_message.delete()
        with open(
            PATH,
            loading_mode.write_override,
            encoding=encoding_type.utf8,
        ) as f:
            yaml.dump(nodes.value, f, indent=2, sort_keys=False)

    @staticmethod
    def create_embed(data: LFGDict) -> discord.Embed:
        embed = LFGEmbed()
        embed.add_field(
            name="遊び方",
            value=data["playing"],
        )
        embed.add_field(
            name="使用VC",
            value=dpy_util.mention(
                mention_type.channel,
                nullable(data.get(params.lfg_dict_keys.vc_id)),
            ),
        )
        embed.add_field(
            name="名目",
            value=data.get(params.lfg_dict_keys.purpose),
        )
        embed.add_field(
            name="時間",
            value=data.get(params.lfg_dict_keys.time),
        )
        embed.add_field(
            name="人数",
            value=data.get(params.lfg_dict_keys.players),
        )
        if (note := data.get(params.lfg_dict_keys.note)) is not None:
            embed.add_field(
                name="● 備考",
                value=note,
            )
        return embed


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LFGCog(bot))
