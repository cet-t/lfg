from enum import Enum, StrEnum
from typing import Final, NotRequired, Optional, TypedDict
from discord import app_commands


class Playing(StrEnum):
    ナワバリ = "ナワバリ"
    バンカラ = "バンカラ"
    バイト = "バイト"
    プラベ = "プラベ"
    なんでも = "なんでも"
    トリカラ = "トリカラ"
    オープン = "オープン"


class Camp(StrEnum):
    フウカ = "フウカ"
    マンタロー = "マンタロー"
    ウツホ = "ウツホ"


def get_players_choices(min: int, max: int) -> list[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=f"@{i}", value=f"@{i}") for i in range(min, max + 1, 1)
    ]


class LFGDict(TypedDict):
    recruiter_id: int
    playing: Playing | str
    camp: Optional[Camp]
    vc_id: int
    purpose: str
    time: str
    players: str
    note: Optional[str]


class LFGListDict(TypedDict):
    lfgs: list[LFGDict]


class MidnightTimeDict(TypedDict):
    start: str
    end: str
