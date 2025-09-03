from enum import IntEnum

from msgspec import Struct


class PmEType(IntEnum):
    credit_card = 0
    bank = 1
    cash = 2
    web_wallet = 3
    web_wallet1 = 4
    IFSC = 5


class Resp(Struct):
    payMethodId: int
    name: str
    template: int
    bankType: int
    color: str
    bankImage: str | None
    bankImageWeb: str | None
    defaultName: str | None = None
