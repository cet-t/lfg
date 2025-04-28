from typing import Optional, TypedDict


class LFGDict(TypedDict):
    recruiter_id: int
    playing: str
    vc_id: int
    purpose: str
    time: str
    players: int
    note: Optional[str]


class LFGListDict(TypedDict):
    lfgs: list[LFGDict]


"""
 {
        "key": "52gal",
        "aliases": [
            "50",
            "52_gal"
        ],
        "type": {
            "key": "shooter",
            "aliases": [],
            "name": {
                "en_US": "Shooters",
                "ja_JP": "シューター"
            }
        },
        "name": {
            "en_US": ".52 Gal",
            "ja_JP": ".52ガロン"
        },
        "main": "52gal",
        "sub": {
            "key": "splashshield",
            "aliases": [],
            "name": {
                "en_US": "Splash Wall",
                "ja_JP": "スプラッシュシールド"
            }
        },
        "special": {
            "key": "megaphone51",
            "aliases": [],
            "name": {
                "en_US": "Killer Wail 5.1",
                "ja_JP": "メガホンレーザー5.1ch"
            }
        },
        "reskin_of": "52gal"
    },
"""


class NameDict(TypedDict):
    en_US: str
    ja_JP: str


class TypeDict(TypedDict):
    key: str
    aliases: list[str]
    name: NameDict


class SubDict(TypedDict):
    key: str
    aliases: list[str]
    name: NameDict


class SpecialDict(TypedDict):
    key: str
    aliases: list[str]
    name: NameDict


class WeaponDict(TypedDict):
    key: str
    aliases: list[str]
    type: TypeDict
    name: NameDict
    main: str
    sub: SubDict
    special: SpecialDict
    reskin_of: Optional[str]


class WeaponsDict(TypedDict):
    weapons: list[WeaponDict]
