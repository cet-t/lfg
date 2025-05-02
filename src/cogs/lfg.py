from datetime import datetime
from typing import Any, Optional
import discord
from discord import app_commands
from discord.ext import commands

from data import Camp, LFGDict, Playing, get_players_choices
from envv import any_ids, fest_ids, arbeit_ids, lobby_ids, roles
import utils.dpy_utils
from utils.values import params
from utils.dpy_utils import (
    create_error_embed,
    datetime_format,
    mention,
    mention_type,
)


class LFGEmbed(discord.Embed):
    def add_field(self, name: Any, value: Any, inline: bool = False) -> "LFGEmbed":
        return super().add_field(name=f"● {name}", value=value, inline=inline)


class LFGCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(__name__)

    @property
    def __is_midnight(self) -> bool:
        return 1 <= datetime.now().hour < 7

    def __create_notify_lines(
        self, role_mention: str, node: LFGDict, vc: discord.VoiceChannel
    ) -> list[str]:
        lines = [
            role_mention,
            f"【遊び方】{node.get(params.lfg_dict_keys.playing)}",
            f"【使用VC】{vc.name}",
            f"【名目】{node.get(params.lfg_dict_keys.purpose)}",
            f"【時間】{node.get(params.lfg_dict_keys.time)}",
            f"【人数】{node.get(params.lfg_dict_keys.players)}",
        ]
        if (note := node.get(params.lfg_dict_keys.note)) is not None:
            lines.append(f"【備考】{note}")
        return lines

    def __get_mention(self, guild: Optional[discord.Guild]) -> str:
        return (
            mention(
                mention_type.role,
                roles.get(guild.id),  # type: ignore
            )
            if self.__is_midnight
            else "@everyone"
        )

    def __create_notify_content(
        self,
        guild: Optional[discord.Guild],
        node: LFGDict,
        vc: discord.VoiceChannel,
    ) -> str:
        return str.join(
            "\n",
            self.__create_notify_lines(
                self.__get_mention(guild),
                node,
                vc,
            ),
        )

    def __create_thread(
        self,
        node: LFGDict,
        message: discord.Message,
        thread_name: Optional[str],
    ):
        return message.create_thread(
            name=(
                thread_name
                if thread_name is not None
                else node.get(
                    params.lfg_dict_keys.purpose,
                    datetime.now().__format__(datetime_format.yyyymmddhhmmss),
                )
            )
        )

    @app_commands.command(name="ロビー募集")
    @app_commands.describe(
        playing="遊び方",
        vc="使用VC",
        purpose="名目",
        time="時間",
        players="人数",
        note="備考",
        thread_name="スレッド名",
    )
    @app_commands.choices(
        playing=[
            app_commands.Choice(name="ナワバリ", value="ナワバリ"),
            app_commands.Choice(name="バンカラ", value="バンカラ"),
            app_commands.Choice(name="プラベ", value="プラベ"),
        ],
        players=get_players_choices(1, 10),
    )
    async def lfg_lobby(
        self,
        interaction: discord.Interaction,
        playing: app_commands.Choice[str],
        vc: discord.VoiceChannel,
        purpose: str,
        time: str,
        players: app_commands.Choice[str],
        note: Optional[str] = None,
        thread_name: Optional[str] = None,
    ) -> None:
        if interaction.channel.id not in lobby_ids:  # type: ignore
            return await interaction.response.send_message(
                embed=create_error_embed(
                    interaction.guild,  # type: ignore
                    "ここじゃだめー",
                ),
                ephemeral=True,
            )
        node = LFGDict(
            recruiter_id=interaction.user.id,
            playing=Playing(playing.value),
            camp=None,
            vc_id=vc.id,
            purpose=purpose,
            time=time,
            players=players.value,
            note=note,
        )
        embed = await LFGCog.create_embed(node)
        await utils.dpy_utils.set_info(
            embed,
            interaction.guild,
            interaction.user,
        )
        response = await interaction.response.send_message(
            allowed_mentions=discord.AllowedMentions.all(),
            content=self.__create_notify_content(interaction.guild, node, vc),
        )
        message = await interaction.channel.fetch_message(response.message_id)  # type: ignore
        await message.edit(
            content=self.__get_mention(interaction.guild),
            embed=embed,
            allowed_mentions=discord.AllowedMentions.all(),
        )
        thread = await self.__create_thread(node, message, thread_name)
        await thread.add_user(interaction.user)

    @app_commands.command(name="サモラン募集")
    @app_commands.describe(
        vc="使用VC",
        purpose="名目",
        time="時間",
        players="人数",
        note="備考",
        thread_name="スレッド名",
    )
    @app_commands.choices(players=get_players_choices(1, 3))
    async def lfg_arbeit(
        self,
        interaction: discord.Interaction,
        vc: discord.VoiceChannel,
        purpose: str,
        time: str,
        players: app_commands.Choice[str],
        note: Optional[str] = None,
        thread_name: Optional[str] = None,
    ) -> None:
        if interaction.channel.id not in arbeit_ids:  # type: ignore
            return await interaction.response.send_message(
                embed=create_error_embed(
                    interaction.guild,  # type: ignore
                    "ここじゃだめー",
                ),
                ephemeral=True,
            )
        node = LFGDict(
            recruiter_id=interaction.user.id,
            playing=Playing.バイト,
            camp=None,
            vc_id=vc.id,
            purpose=purpose,
            time=time,
            players=players.value,
            note=note,
        )
        embed = await LFGCog.create_embed(node)
        await utils.dpy_utils.set_info(
            embed,
            interaction.guild,
            interaction.user,
        )
        response = await interaction.response.send_message(
            allowed_mentions=discord.AllowedMentions.all(),
            content=self.__create_notify_content(interaction.guild, node, vc),
        )
        message = await interaction.channel.fetch_message(response.message_id)  # type: ignore
        await message.edit(
            content=self.__get_mention(interaction.guild),
            embed=embed,
            allowed_mentions=discord.AllowedMentions.all(),
        )
        thread = await self.__create_thread(node, message, thread_name)
        await thread.add_user(interaction.user)

    @app_commands.command(name="その他募集")
    @app_commands.describe(
        playing="遊び方",
        vc="使用VC",
        purpose="名目",
        time="時間",
        players="人数",
        note="備考",
        thread_name="スレッド名",
    )
    async def lfg_any(
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
        if interaction.channel.id not in any_ids:  # type: ignore
            return await interaction.response.send_message(
                embed=create_error_embed(
                    interaction.guild,  # type: ignore
                    "ここじゃだめー",
                ),
                ephemeral=True,
            )
        node = LFGDict(
            recruiter_id=interaction.user.id,
            playing=playing,
            camp=None,
            vc_id=vc.id,
            purpose=purpose,
            time=time,
            players=f"@{players}",
            note=note,
        )
        embed = await LFGCog.create_embed(node)
        await utils.dpy_utils.set_info(
            embed,
            interaction.guild,
            interaction.user,
        )
        response = await interaction.response.send_message(
            allowed_mentions=discord.AllowedMentions.all(),
            content=self.__create_notify_content(interaction.guild, node, vc),
        )
        message = await interaction.channel.fetch_message(response.message_id)  # type: ignore
        await message.edit(
            content=self.__get_mention(interaction.guild),
            embed=embed,
            allowed_mentions=discord.AllowedMentions.all(),
        )
        thread = await self.__create_thread(node, message, thread_name)
        await thread.add_user(interaction.user)

    @app_commands.command(name="フェス募集")
    @app_commands.describe(
        playing="遊び方",
        camp="陣営",
        vc="使用VC",
        purpose="名目",
        time="時間",
        players="人数",
        note="備考",
        thread_name="スレッド名",
    )
    @app_commands.choices(
        playing=[
            app_commands.Choice(name="オープン", value="オープン"),
            app_commands.Choice(name="トリカラ", value="トリカラ"),
        ],
        camp=[
            app_commands.Choice(name="フウカ", value="フウカ"),
            app_commands.Choice(name="マンタロー", value="マンタロー"),
            app_commands.Choice(name="ウツホ", value="ウツホ"),
        ],
        players=get_players_choices(1, 3),
    )
    async def lfg_fest(
        self,
        interaction: discord.Interaction,
        playing: app_commands.Choice[str],
        camp: app_commands.Choice[str],
        vc: discord.VoiceChannel,
        purpose: str,
        time: str,
        players: app_commands.Choice[str],
        note: Optional[str] = None,
        thread_name: Optional[str] = None,
    ) -> None:
        if interaction.channel.id not in fest_ids:  # type: ignore
            return await interaction.response.send_message(
                embed=create_error_embed(
                    interaction.guild,  # type: ignore
                    "ここじゃだめー",
                ),
                ephemeral=True,
            )
        node = LFGDict(
            recruiter_id=interaction.user.id,
            playing=Playing(playing.value),
            camp=Camp(camp.value),
            vc_id=vc.id,
            purpose=purpose,
            time=time,
            players=players.value,
            note=note,
        )
        embed = await LFGCog.create_embed(node)
        await utils.dpy_utils.set_info(
            embed,
            interaction.guild,
            interaction.user,
        )
        role_mention = "@none"
        match node.get(params.lfg_dict_keys.camp):
            case Camp.フウカ:
                role_mention = "@深夜フウカ" if self.__is_midnight else "@フウカ"
            case Camp.マンタロー:
                role_mention = (
                    "@深夜マンタロー" if self.__is_midnight else "@マンタロー"
                )
            case Camp.ウツホ:
                role_mention = "@深夜ウツホ" if self.__is_midnight else "@ウツホ"

        notify_content_lines = [
            role_mention,
            f"【遊び方】{node.get(params.lfg_dict_keys.playing)}",
            f"【陣営】{node.get(params.lfg_dict_keys.camp)}",
            f"【使用VC】{vc.name}",
            f"【名目】{node.get(params.lfg_dict_keys.purpose)}",
            f"【時間】{node.get(params.lfg_dict_keys.time)}",
            f"【人数】{node.get(params.lfg_dict_keys.players)}",
        ]
        if (note := node.get(params.lfg_dict_keys.note)) is not None:
            notify_content_lines.append(f"【備考】{note}")
        response = await interaction.response.send_message(
            allowed_mentions=discord.AllowedMentions.all(),
            content=str.join("\n", notify_content_lines),
        )
        message = await interaction.channel.fetch_message(response.message_id)  # type: ignore
        await message.edit(
            content=role_mention,
            embed=embed,
            allowed_mentions=discord.AllowedMentions.all(),
        )
        thread = await self.__create_thread(node, message, thread_name)
        await thread.add_user(interaction.user)

    @staticmethod
    async def create_embed(data: LFGDict) -> discord.Embed:
        embed = LFGEmbed()
        embed.add_field(name="遊び方", value=data.get(params.lfg_dict_keys.playing))
        if (camp := data.get(params.lfg_dict_keys.camp)) is not None:
            embed.add_field(name="陣営", value=camp)
        embed.add_field(
            name="使用VC",
            value=utils.dpy_utils.mention(
                mention_type.channel, data.get(params.lfg_dict_keys.vc_id)
            ),
        )
        embed.add_field(name="名目", value=data.get(params.lfg_dict_keys.purpose))
        embed.add_field(name="時間", value=data.get(params.lfg_dict_keys.time))
        embed.add_field(name="人数", value=data.get(params.lfg_dict_keys.players))
        if (note := data.get(params.lfg_dict_keys.note)) is not None:
            embed.add_field(name="備考", value=note)
        return embed


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LFGCog(bot))
