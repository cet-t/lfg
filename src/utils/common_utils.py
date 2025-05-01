from array import array
from enum import StrEnum


class datetime_format(StrEnum):
    yyyymmdd = "%Y/%m/%d"
    yyyymmddhhmmss = yyyymmdd + " %H:%M:%S"


class file_mode(StrEnum):
    read = "r"
    write_override = "w"
    read_new = "x"
    write_append = "a"


class encoding_type(StrEnum):
    utf8 = "utf-8"
    shiftjis = "shift_jis"
    eucjis = "euc_jp"
    iso2022jp = "iso2022_jp"


def is_empty(source: list | dict | array) -> bool:
    return len(source) <= 0
