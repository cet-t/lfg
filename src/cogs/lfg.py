from datetime import datetime
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
    get_players_choices,
)
from envv import (
    any_ch_ids,
    any_vc_ids,
    arbeit_vc_ids,
    pinned_ch_ids,
    fest_vc_ids,
    arbeit_ch_ids,
    fuka_vc_ids,
    guild_ids,
    lobby_ch_ids,
    lobby_vc_ids,
    manta_vc_ids,
    pinned_message_path,
    midnight_role_ids,
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
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # data: Optional[PinnedMessagesDict] = None
        # exists = os.path.exists(pinned_message_path)
        # if not exists:
        #     data = PinnedMessagesDict(pinned_messages=[])
        #     for _, ids in pinned_ch_ids.items():
        #         for id in ids:
        #             data["pinned_messages"].append(
        #                 PinnedMessageDict(channel_id=id, message_id=None)
        #             )
        #     with open(pinned_message_path, "x") as f:
        #         json.dump(data, f, indent=2)
        # else:
        #     with open(pinned_message_path, "r") as f:
        #         data = PinnedMessagesDict(json.load(f))
        # if data is not None:
        #     guild = await self.bot.fetch_guild(guild_ids["release"])
        #     for i in range(len(data["pinned_messages"])):
        #         channel = await guild.fetch_channel(
        #             data["pinned_messages"][i]["channel_id"]
        #         )
        #         message_id: int | None = None
        #         if data["pinned_messages"][i]["message_id"] is None:
        #             # 送信
        #             message = await channel.send("募集はこちらをタップ☞/rsth")  # type: ignore
        #             message_id = message.id
        #         # else:
        #         #     message = await channel.fetch_message(data["pinned_messages"][i]["message_id"])  # type: ignore
        #         #     new_message = await message.edit(content="test2")
        #         #     message_id = new_message.id
        #         data["pinned_messages"][i]["message_id"] = message_id
        # with open(pinned_message_path, "w") as f:
        #     json.dump(data, f, indent=2)

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

    @app_commands.command(name="set_pinned_message")
    @app_commands.describe(category="カテゴリ")
    @app_commands.choices(
        category=[
            app_commands.Choice(name="ロビー", value="lobby"),
            app_commands.Choice(name="バイト", value="beit"),
            app_commands.Choice(name="その他", value="any"),
            app_commands.Choice(name="フェス", value="fest"),
        ]
    )
    async def set_pinned_message(
        self,
        interaction: discord.Interaction,
        category: app_commands.Choice[str],
    ):
        content = "募集はこちらをタップ☞"
        match category.value:
            case "lobby":
                content = "</ロビー募集:1367780421248749701>"
            case "beit":
                content = "</バイト募集:1369647448779128863>"
            case "any":
                content = "</その他募集:1367879652365963405>"
            case "fest":
                content = "</フェス募集:1367766800024080434>"
        if not content.endswith(">"):
            await interaction.response.send_message(
                embed=create_error_embed(interaction.guild, "あれー？"),  # type: ignore
                ephemeral=True,
            )
        else:
            data: Optional[PinnedMessagesDict] = None
            setupable = False
            if not os.path.exists(pinned_message_path):
                data = PinnedMessagesDict(pinned_messages=[])
                with open(pinned_message_path, "x") as f:
                    json.dump(data, f, indent=2)
                setupable = True
            else:
                with open(pinned_message_path, "r") as f:
                    data = PinnedMessagesDict(json.load(f))
                for item in data["pinned_messages"]:
                    if item["channel_id"] == interaction.channel.id:  # type: ignore
                        if item["message_id"] is not None:
                            setupable = False
            if setupable:
                pass
            message = await interaction.channel.send(content)  # type: ignore
            if data is not None and interaction.channel is not None:
                item = PinnedMessageDict(
                    channel_id=interaction.channel.id,
                    message_id=message.id,
                )
                for i in range(len(data["pinned_messages"])):
                    if data["pinned_messages"][i]["channel_id"] == item["channel_id"]:
                        data["pinned_messages"][i]["message_id"] = item["message_id"]
                        break
            with open(pinned_message_path, "w") as f:
                json.dump(data, f, indent=2)
            # with open(pinned_message_path, "r") as f:
            #     data = PinnedMessagesDict(json.load(f))
            # for i in range(len(data["pinned_messages"])):
            #     if data["pinned_messages"][i]["channel_id"] == interaction.channel_id:
            #         data["pinned_messages"][i]["message_id"] = message.id
            #         break
            # with open(pinned_message_path, "w") as f:
            #     json.dump(data, f, indent=2)

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
        if interaction.channel.id not in lobby_ch_ids:  # type: ignore
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

        if interaction.guild is not None and os.path.exists(pinned_message_path):
            with open(pinned_message_path, "r") as f:
                data = PinnedMessagesDict(json.load(f))
            if data is None:
                return
            for i in range(len(data["pinned_messages"])):
                if interaction.channel_id == data["pinned_messages"][i]["channel_id"]:
                    try:
                        old_message = await interaction.channel.fetch_message(data["pinned_messages"][i]["message_id"])  # type: ignore
                        content = old_message.content
                        await old_message.delete()
                    except:
                        pass
                    new_message = await interaction.channel.send(content)  # type: ignore
                    data["pinned_messages"][i]["message_id"] = new_message.id
                    with open(pinned_message_path, "w") as f:
                        json.dump(data, f, indent=2)
                    break

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
        if interaction.channel.id not in arbeit_ch_ids:  # type: ignore
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
        if interaction.channel.id not in fest_vc_ids:  # type: ignore
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
