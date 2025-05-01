from typing import NotRequired, Optional, TypedDict


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


# class RoleIDDict(TypedDict):
#     midnight: NotRequired[int]


# class RoleIDsDict(TypedDict):
#     roles: dict[int, RoleIDDict]


class MidnightTimeDict(TypedDict):
    start: str
    end: str
