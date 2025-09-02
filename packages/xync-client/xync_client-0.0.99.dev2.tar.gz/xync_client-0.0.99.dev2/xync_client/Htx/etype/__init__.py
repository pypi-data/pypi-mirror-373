from msgspec import Struct


class Country(Struct):
    id: int
    code: int
    short: str
    name: str
    cur_id: str
