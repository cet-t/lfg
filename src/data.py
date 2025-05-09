from enum import Enum, StrEnum
import json
from typing import Optional, TypedDict
from discord import app_commands

from envv import exists_pinned_message_path, pinned_message_path


class PlayingType(Enum):
    lobby = 0
    arbeit = 1
    other = 2
    fest = 3


class Playing(StrEnum):
    lobby_nawabari = "ナワバリ"
    lobby_bankara = "バンカラ"
    lobby_event = "イベント"
    lobby_private = "プラベ"
    lobby_any = "なんでも"

    kuma_beit = "バイト"
    kuma_newbie = "バイト(達人以下のみ)"
    kuma_valuation = "バイト(評価上げ)"
    kuma_private = "プラベバイト"

    fest_tricolor = "トリカラ"
    fest_open = "オープン"


class Camp(StrEnum):
    Fuka = "フウカ"
    Mantaro = "マンタロー"
    Utsuho = "ウツホ"


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


class PinnedMessageDict(TypedDict):
    channel_id: int
    message_id: Optional[int]


class PinnedMessagesDict(TypedDict):
    pinned_messages: list[PinnedMessageDict]


def try_write_pinned_messages(data: PinnedMessagesDict) -> bool:
    """
    ファイルに書き込み
    """
    try:
        if not exists_pinned_message_path():
            return False

        with open(pinned_message_path, "w") as f:
            json.dump(data, f, indent=2)
    except:
        return False
    return True
