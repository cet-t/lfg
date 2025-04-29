from datetime import datetime
from enum import Enum, StrEnum

import discord

from utils.nullable import nullable


class mention_type(Enum):
    none = 0
    user = 1
    channel = 2


class datetime_format(StrEnum):
    yyyymmdd = "%Y/%m/%d"
    yyyymmddhhmmss = yyyymmdd + " %H:%M:%S"


class loading_mode(StrEnum):
    read = "r"
    write_override = "w"
    read_new = "x"
    write_append = "a"


class encoding_type(StrEnum):
    utf8 = "utf-8"
    shiftjis = "shift_jis"
    eucjis = "euc_jp"
    iso2022jp = "iso2022_jp"


class dpy_util:
    @staticmethod
    def code_block(text) -> str:
        return f"```{text}```"

    @staticmethod
    def inline_code_block(text) -> str:
        return f"`{text}`"

    @staticmethod
    def heading(lv: int, text) -> str:
        if not (1 <= lv <= 4):
            return text.__str__()
        return f"{str.join("", ["#" for _ in range(lv)])} {text}"  # type: ignore

    @staticmethod
    def mention(type: mention_type, id: nullable[int]) -> str:
        if not id.has_value:
            return id.__str__()
        match type:
            case mention_type.none:
                return id.__str__()
            case mention_type.user:
                return f"<@{id}>"
            case mention_type.channel:
                return f"<#{id}>"

    @staticmethod
    def add_code_field(embed: discord.Embed, name, value, inline: bool = False) -> None:
        embed.add_field(
            name=name.__str__(),
            value=dpy_util.code_block(value),
            inline=inline,
        )

    @staticmethod
    def set_author(
        embed: discord.Embed,
        member: discord.Member | None,
    ) -> discord.Embed:
        if member is not None:
            embed.set_author(
                name=member.display_name,
                icon_url=member.display_icon,
            )
        return embed

    @staticmethod
    def set_footer(embed: discord.Embed, guild: discord.Guild | None) -> discord.Embed:
        if guild is not None:
            embed.set_footer(
                text=datetime.now().__format__(datetime_format.yyyymmddhhmmss),
                icon_url=guild.icon,
            )
        return embed

    @staticmethod
    async def set_info(
        embed: discord.Embed,
        guild: discord.Guild | None,
        user: discord.User | discord.Member | None,
        bot: discord.ClientUser | None,
    ) -> discord.Embed:
        if guild is not None and user is not None and bot is not None:
            member = await guild.fetch_member(user.id)
            embed.set_author(
                name=member.display_name,
                icon_url=user.avatar.url,  # type: ignore
            )
            embed.set_footer(
                text=f"{guild.name} - {datetime.now().__format__(datetime_format.yyyymmddhhmmss)}",
                icon_url=guild.icon,
            )
        return embed
