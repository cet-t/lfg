from typing import Final, overload


class file_path:
    roles_yml: Final = "./data/roles.yml"


class api_url:
    stat_ink_weapon: Final = "https://stat.ink/api/v3/weapon"
    stat_ink_stage: Final = "https://stat.ink/api/v3/stage"

    yuu26_schedule: Final = "https://spla3.yuu26.com/api/schedule"
    yuu26_schedule_open_now: Final = "https://spla3.yuu26.com/api/bankara-open/now"
    yuu26_schedule_open_next: Final = "https://spla3.yuu26.com/api/bankara-open/next"
    yuu26_schedule_fest_open_now: Final = "https://spla3.yuu26.com/api/fest/schedule"
    yuu26_schedule_fest_tri_now: Final = "https://spla3.yuu26.com/api/fest/tri/now"


class params:
    class lfg_dict_keys:
        recruiter_id: Final[str] = "recruiter_id"
        playing: Final[str] = "playing"
        vc_id: Final[str] = "vc_id"
        purpose: Final[str] = "purpose"
        time: Final[str] = "time"
        players: Final[str] = "players"
        note: Final[str] = "note"
