from datetime import datetime
from enum import Enum
from typing import Any, Optional

import discord

from utils.common_utils import datetime_format, is_empty


class mention_type(Enum):
    none = 0
    user = 1
    channel = 2
    role = 3


def code_block(text) -> str:
    return f"```{text}```"


def inline_code_block(text) -> str:
    return f"`{text}`"


def heading(lv: int, text) -> str:
    if not (1 <= lv <= 4):
        return text.__str__()
    return f"{str.join("", ["#" for _ in range(lv)])} {text}"  # type: ignore


def mention(type: mention_type, id: Optional[int]) -> str:
    if id is None:
        return id.__str__()
    match type:
        case mention_type.none:
            return id.__str__()
        case mention_type.user:
            return f"<@{id}>"
        case mention_type.channel:
            return f"<#{id}>"
        case mention_type.role:
            return f"<@&{id}>"


def add_code_field(embed: discord.Embed, name, value, inline: bool = False) -> None:
    embed.add_field(
        name=name.__str__(),
        value=code_block(value),
        inline=inline,
    )


def set_author(
    embed: discord.Embed,
    member: Optional[discord.Member],
) -> discord.Embed:
    if member is not None:
        embed.set_author(
            name=member.display_name,
            icon_url=member.display_icon,
        )
    return embed


def set_footer(embed: discord.Embed, guild: Optional[discord.Guild]) -> discord.Embed:
    if guild is not None:
        embed.set_footer(
            text=datetime.now().__format__(datetime_format.yyyymmddhhmmss),
            icon_url=guild.icon,
        )
    return embed


async def set_info(
    embed: discord.Embed,
    guild: Optional[discord.Guild],
    user: Optional[discord.User | discord.Member],
) -> None:
    if guild is not None and user is not None:
        member = await guild.fetch_member(user.id)
        embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar,
        )
        embed.set_footer(
            text=f"{guild.name} - {datetime.now().__format__(datetime_format.yyyymmddhhmmss)}",
            icon_url=guild.icon,
        )


async def check_admin(
    guild: Optional[discord.Guild],
    user: Optional[discord.User | discord.Member],
    admin_role: Optional[discord.Role] = None,
) -> bool:
    if guild is None or user is None:
        return False
    is_admin = False
    member = await guild.fetch_member(user.id)
    if admin_role is None:
        is_admin = is_empty(
            list(
                filter(
                    lambda role: role.permissions.administrator,
                    member.roles,
                )
            )
        )
    else:
        for role in member.roles:
            if role.id == admin_role.id:
                is_admin = True
                break
    return is_admin


def create_log_embed(guild: discord.Guild, value: Any) -> discord.Embed:
    embed = discord.Embed(
        title="LOG",
        description=value,
        colour=discord.Colour.green(),
    )
    set_footer(embed, guild)
    return embed


def create_error_embed(guild: discord.Guild, value: Any) -> discord.Embed:
    embed = discord.Embed(
        title="ERROR",
        description=value,
        colour=discord.Colour.red(),
    )
    set_footer(embed, guild)
    return embed
