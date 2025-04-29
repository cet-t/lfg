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
