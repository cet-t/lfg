from datetime import datetime
from genericpath import exists
import json
import os
from typing import Any, Optional
import discord
from discord import app_commands
from discord.ext import commands

from data import (
    Camp,
    LFGDict,
    PinnedMessageDict,
    PinnedMessagesDict,
    Playing,
    PlayingType,
    get_players_choices,
)
from envv import (
    any_ch_ids,
    any_vc_ids,
    arbeit_vc_ids,
    cat_ids_types,
    exists_pinned_message_path,
    pinned_ch_ids,
    fest_ch_ids,
    arbeit_ch_ids,
    fuka_vc_ids,
    guild_ids,
    lobby_ch_ids,
    lobby_vc_ids,
    manta_vc_ids,
    pinned_message_path,
    midnight_role_ids,
    pinned_cmd_links,
    utuho_vc_ids,
)
import utils.dpy_utils
from utils.values import params
from utils.dpy_utils import (
    create_error_embed,
    create_log_embed,
    datetime_format,
    mention,
    mention_type,
)


class LFGEmbed(discord.Embed):
    def add_field(self, name: Any, value: Any, inline: bool = False) -> "LFGEmbed":
        return super().add_field(name=f"● {name}", value=value, inline=inline)


class LFGCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        data = PinnedMessagesDict(pinned_messages=[])
        if exists := exists_pinned_message_path():
            with open(pinned_message_path, "r") as f:
                data = PinnedMessagesDict(json.load(f))

        guild = await self.bot.fetch_guild(guild_ids["release"])

        # 新規作成
        if len(data["pinned_messages"]) <= 0:
            for playing_type, channel_ids in pinned_ch_ids.items():
                command_link = pinned_cmd_links[playing_type]
                for channel_id in channel_ids:
                    ch = await guild.fetch_channel(channel_id)
                    message = await ch.send(command_link)  # type: ignore
                    data["pinned_messages"].append(
                        PinnedMessageDict(channel_id=channel_id, message_id=message.id)
                    )
        with open(pinned_message_path, "w" if exists else "x") as f:
            json.dump(data, f, indent=2)

        print(__name__)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        await self.__update_pinned_message(message)

    def __try_save_data(self, data: PinnedMessagesDict) -> bool:
        try:
            if exists_pinned_message_path():
                with open(pinned_message_path, "w") as f:
                    json.dump(data, f, indent=2)
        except:
            return False
        return True

    async def __update_pinned_message(self, message: discord.Message) -> None:
        """
        固定メッセージの更新
        """
        # メッセージが一時的 or ファイルが存在しない
        if message.flags.ephemeral or not exists_pinned_message_path():
            return

        with open(pinned_message_path) as f:
            data = PinnedMessagesDict(json.load(f))

        # 対象チャンネル内か確認
        channel_ids = [item["channel_id"] for item in data["pinned_messages"]]
        if message.channel.id not in channel_ids:  # 対象チャンネル外
            return

        message_ids = [item["message_id"] for item in data["pinned_messages"]]
        # 自分自身が送信した固定メッセージではない(ファイルにチャンネルIDが存在しない)
        if message.id not in message_ids:
            for i in range(len(data["pinned_messages"])):
                pinned_message = data["pinned_messages"][i]
                category_id = int(message.channel.category_id)  # type: ignore
                command_link = pinned_cmd_links[cat_ids_types[category_id]]
                if pinned_message["message_id"] is not None:
                    if message.channel.id == pinned_message["channel_id"]:
                        old_message_id = pinned_message["message_id"]
                        try:
                            # 通知用に一度メッセージを削除しているので一回目は例外
                            old_message = await message.channel.fetch_message(old_message_id)  # type: ignore
                            await old_message.delete()
                        except discord.NotFound:
                            return
                        new_message = await message.channel.send(command_link)
                        data["pinned_messages"][i]["message_id"] = new_message.id
                        break
                else:
                    new_message = await message.channel.send(command_link)
                    data["pinned_messages"][i]["message_id"] = new_message.id
                    break
            with open(pinned_message_path, "w") as f:
                json.dump(data, f, indent=2)

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
                midnight_role_ids.get(guild.id),  # type: ignore
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
        name = (
            thread_name
            if thread_name is not None
            else node.get(
                params.lfg_dict_keys.purpose,
                datetime.now().__format__(datetime_format.yyyymmddhhmmss),
            )
        )
        if len(name) >= 100:
            name = name[:100]
        return message.create_thread(name=name)

    @app_commands.command(
        name="delete", description="メッセージを削除(他人のメッセージは削除不可)"
    )
    @app_commands.describe(message_id="メッセージID")
    async def delete(self, interaction: discord.Interaction, message_id: int) -> None:
        delete_user_id = interaction.user.id
        try:
            message = await interaction.channel.fetch_message(message_id)  # type: ignore
        except:
            return await interaction.response.send_message(
                embed=create_error_embed(interaction.guild, "だめー"),  # type: ignore
                ephemeral=True,
            )
        if message.interaction is None or delete_user_id != message.interaction.user.id:
            return await interaction.response.send_message(
                embed=create_error_embed(interaction.guild, "だめー"),  # type: ignore
                ephemeral=True,
            )
        await message.delete()
        await interaction.response.send_message(
            embed=create_log_embed(
                guild=interaction.guild, value="おっけー"  # type: ignore
            ),
            ephemeral=True,
        )

    async def autocomplete_lobby(
        self,
        interaction: discord.Interaction,
        value: str,
    ) -> list[app_commands.Choice[str]]:
        voice_channels = (
            interaction.guild.voice_channels if interaction.guild is not None else []
        )
        if len(voice_channels) < 1:
            return []
        return [
            app_commands.Choice(name=vc.name, value=vc.id.__str__())
            for vc in voice_channels
            if vc.id in lobby_vc_ids
        ]

    @app_commands.command(name="ロビー募集")
    @app_commands.describe(
        playing="遊び方",
        vc_id="使用VC",
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
            app_commands.Choice(name="なんでも", value="なんでも"),
        ],
        players=get_players_choices(1, 10),
    )
    @app_commands.autocomplete(vc_id=autocomplete_lobby)
    async def lfg_lobby(
        self,
        interaction: discord.Interaction,
        playing: app_commands.Choice[str],
        vc_id: str,
        purpose: str,
        time: str,
        players: app_commands.Choice[str],
        note: Optional[str] = None,
        thread_name: Optional[str] = None,
    ) -> None:
        if interaction.channel.id not in pinned_ch_ids[PlayingType.lobby]:  # type: ignore
            return await interaction.response.send_message(
                embed=create_error_embed(
                    interaction.guild,  # type: ignore
                    "ここじゃだめー",
                ),
                ephemeral=True,
            )
        vc: discord.VoiceChannel
        if interaction.guild is not None:
            for voice_channel in interaction.guild.voice_channels:
                if int(vc_id) == voice_channel.id:
                    vc = voice_channel
                    break
        try:
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
        except TypeError:
            return await interaction.response.send_message(
                embed=create_error_embed(
                    interaction.guild,  # type: ignore
                    "あれれ～？",
                )
            )

        # if exists_pinned_message_path():
        #     with open(pinned_message_path) as f:
        #         data = PinnedMessagesDict(json.load(f))
        #         for i in range(len(data["pinned_messages"])):
        #             channel_id = data["pinned_messages"][i]["channel_id"]
        #             message_id = data["pinned_messages"][i]["message_id"]
        #             if interaction.channel_id == channel_id:
        #                 if message_id is not None:
        #                     del_message = await interaction.channel.fetch_message(  # type: ignore
        #                         message_id
        #                     )
        #                     await del_message.delete()
        #                 message = await interaction.channel.send(  # type: ignore
        #                     pinned_cmd_links[PlayingType.lobby]
        #                 )
        #                 data["pinned_messages"][i]["message_id"] = message.id
        #     with open(pinned_message_path, "w") as f:
        #         json.dump(data, f, indent=2)

    async def autocomplete_arbeit(
        self,
        interaction: discord.Interaction,
        value: str,
    ) -> list[app_commands.Choice[str]]:
        voice_channels = (
            interaction.guild.voice_channels if interaction.guild is not None else []
        )
        if len(voice_channels) < 1:
            return []
        return [
            app_commands.Choice(name=vc.name, value=vc.id.__str__())
            for vc in voice_channels
            if vc.id in arbeit_vc_ids
        ]

    @app_commands.command(name="バイト募集")
    @app_commands.describe(
        playing="遊び方",
        vc_id="使用VC",
        purpose="名目",
        time="時間",
        players="人数",
        note="備考",
        thread_name="スレッド名",
    )
    @app_commands.choices(
        playing=[
            app_commands.Choice(name="バイト", value="バイト"),
            app_commands.Choice(
                name="バイト(達人以下のみ)", value="バイト(達人以下のみ)"
            ),
            app_commands.Choice(name="バイト(評価上げ)", value="バイト(評価上げ)"),
            app_commands.Choice(name="プラベバイト", value="プラベバイト"),
        ],
        players=get_players_choices(1, 3),
    )
    @app_commands.autocomplete(vc_id=autocomplete_arbeit)
    async def lfg_arbeit(
        self,
        interaction: discord.Interaction,
        playing: app_commands.Choice[str],
        vc_id: str,
        purpose: str,
        time: str,
        players: app_commands.Choice[str],
        note: Optional[str] = None,
        thread_name: Optional[str] = None,
    ) -> None:
        if interaction.channel.id not in pinned_ch_ids[PlayingType.arbeit]:  # type: ignore
            return await interaction.response.send_message(
                embed=create_error_embed(
                    interaction.guild,  # type: ignore
                    "ここじゃだめー",
                ),
                ephemeral=True,
            )
        vc: discord.VoiceChannel
        if interaction.guild is not None:
            for voice_channel in interaction.guild.voice_channels:
                if int(vc_id) == voice_channel.id:
                    vc = voice_channel
                    break
        node = LFGDict(
            recruiter_id=interaction.user.id,
            playing=playing.value,
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

        # if exists_pinned_message_path():
        #     with open(pinned_message_path) as f:
        #         data = PinnedMessagesDict(json.load(f))
        #         for i in range(len(data["pinned_messages"])):
        #             channel_id = data["pinned_messages"][i]["channel_id"]
        #             message_id = data["pinned_messages"][i]["message_id"]
        #             if interaction.channel_id == channel_id:
        #                 if message_id is not None:
        #                     del_message = await interaction.channel.fetch_message(  # type: ignore
        #                         message_id
        #                     )
        #                     await del_message.delete()
        #                 message = await interaction.channel.send(  # type: ignore
        #                     pinned_cmd_links[PlayingType.arbeit]
        #                 )
        #                 data["pinned_messages"][i]["message_id"] = message.id
        #     with open(pinned_message_path, "w") as f:
        #         json.dump(data, f, indent=2)

    async def autocomplete_any(
        self,
        interaction: discord.Interaction,
        value: str,
    ) -> list[app_commands.Choice[str]]:
        voice_channels = (
            interaction.guild.voice_channels if interaction.guild is not None else []
        )
        if len(voice_channels) < 1:
            return []
        return [
            app_commands.Choice(name=vc.name, value=vc.id.__str__())
            for vc in voice_channels
            if vc.id in any_vc_ids
        ]

    @app_commands.command(name="その他募集")
    @app_commands.describe(
        playing="遊び方",
        vc_id="使用VC",
        purpose="名目",
        time="時間",
        players="人数",
        note="備考",
        thread_name="スレッド名",
    )
    @app_commands.autocomplete(vc_id=autocomplete_any)
    async def lfg_any(
        self,
        interaction: discord.Interaction,
        playing: str,
        vc_id: str,
        purpose: str,
        time: str,
        players: int,
        note: Optional[str] = None,
        thread_name: Optional[str] = None,
    ) -> None:
        if interaction.channel.id not in any_ch_ids:  # type: ignore
            return await interaction.response.send_message(
                embed=create_error_embed(
                    interaction.guild,  # type: ignore
                    "ここじゃだめー",
                ),
                ephemeral=True,
            )
        vc: discord.VoiceChannel
        if interaction.guild is not None:
            for voice_channel in interaction.guild.voice_channels:
                if int(vc_id) == voice_channel.id:
                    vc = voice_channel
                    break
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

        # if exists_pinned_message_path():
        #     with open(pinned_message_path) as f:
        #         data = PinnedMessagesDict(json.load(f))
        #         for i in range(len(data["pinned_messages"])):
        #             channel_id = data["pinned_messages"][i]["channel_id"]
        #             message_id = data["pinned_messages"][i]["message_id"]
        #             if interaction.channel_id == channel_id:
        #                 if message_id is not None:
        #                     del_message = await interaction.channel.fetch_message(  # type: ignore
        #                         message_id
        #                     )
        #                     await del_message.delete()
        #                 message = await interaction.channel.send(  # type: ignore
        #                     pinned_cmd_links[PlayingType.other]
        #                 )
        #                 data["pinned_messages"][i]["message_id"] = message.id
        #     with open(pinned_message_path, "w") as f:
        #         json.dump(data, f, indent=2)

    async def autocomplete_fest(self, interaction: discord.Interaction, value: str):
        if (guild := interaction.guild) is None or interaction.data is None:
            return list[app_commands.Choice]()
        try:
            camp_str = interaction.data.get("options", [{}])[1].get("value")
            if camp_str is None:
                return list[app_commands.Choice]()

            vc_ids = []
            match Camp(camp_str):
                case Camp.Mantaro:
                    vc_ids = manta_vc_ids
                case Camp.Fuka:
                    vc_ids = fuka_vc_ids
                case Camp.Utsuho:
                    vc_ids = utuho_vc_ids
            return [
                app_commands.Choice(name=vc.name, value=vc.id.__str__())
                for vc in guild.voice_channels
                if vc.id in vc_ids
            ]
        except IndexError:
            return list[app_commands.Choice]()

    @app_commands.command(name="フェス募集")
    @app_commands.describe(
        playing="遊び方",
        camp="陣営",
        vc_id="使用VC",
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
    @app_commands.autocomplete(vc_id=autocomplete_fest)
    async def lfg_fest(
        self,
        interaction: discord.Interaction,
        playing: app_commands.Choice[str],
        camp: app_commands.Choice[str],
        vc_id: str,
        purpose: str,
        time: str,
        players: app_commands.Choice[str],
        note: Optional[str] = None,
        thread_name: Optional[str] = None,
    ) -> None:
        if interaction.channel.id not in pinned_ch_ids[PlayingType.fest]:  # type: ignore
            return await interaction.response.send_message(
                embed=create_error_embed(
                    interaction.guild,  # type: ignore
                    "ここじゃだめー",
                ),
                ephemeral=True,
            )
        vc: discord.VoiceChannel
        if interaction.guild is not None:
            for voice_channel in interaction.guild.voice_channels:
                if int(vc_id) == voice_channel.id:
                    vc = voice_channel
                    break

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
            case Camp.Fuka:
                role_mention = (
                    "@深夜フウカ" if self.__is_midnight else "<@&1208184758509641799>"
                )
            case Camp.Mantaro:
                role_mention = (
                    "@深夜マンタロー"
                    if self.__is_midnight
                    else "<@&1208184904869748796>"
                )
            case Camp.Utsuho:
                role_mention = (
                    "@深夜ウツホ" if self.__is_midnight else "<@&1208184866596978698>"
                )

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

        # if exists_pinned_message_path():
        #     with open(pinned_message_path) as f:
        #         data = PinnedMessagesDict(json.load(f))
        #         for i in range(len(data["pinned_messages"])):
        #             channel_id = data["pinned_messages"][i]["channel_id"]
        #             message_id = data["pinned_messages"][i]["message_id"]
        #             if interaction.channel_id == channel_id:
        #                 if message_id is not None:
        #                     del_message = await interaction.channel.fetch_message(  # type: ignore
        #                         message_id
        #                     )
        #                     await del_message.delete()
        #                 message = await interaction.channel.send(  # type: ignore
        #                     pinned_cmd_links[PlayingType.fest]
        #                 )
        #                 data["pinned_messages"][i]["message_id"] = message.id
        #     with open(pinned_message_path, "w") as f:
        #         json.dump(data, f, indent=2)

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
