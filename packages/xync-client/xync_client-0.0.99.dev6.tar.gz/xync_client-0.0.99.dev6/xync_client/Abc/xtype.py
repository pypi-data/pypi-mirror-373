from typing import Literal

from pydantic import BaseModel, model_validator
from x_model.types import BaseUpd
from xync_schema.enums import PmType
from xync_schema.models import Country, Pm, Ex
from xync_schema.xtype import PmExBank

from xync_client.pm_unifier import PmUni

DictOfDicts = dict[int | str, dict]
ListOfDicts = list[dict]
FlatDict = dict[int | str, str]
MapOfIdsList = dict[int | str, list[int | str]]


class PmTrait:
    typ: PmType | None = None
    logo: str | None = None
    banks: list[PmExBank] | None = None


class PmEx(BaseModel, PmTrait):
    exid: int | str
    name: str


class PmIn(BaseUpd, PmUni, PmTrait):
    _unq = "norm", "country"
    country: Country | None = None

    class Config:
        arbitrary_types_allowed = True


class PmExIn(BaseModel):
    pm: Pm
    ex: Ex
    exid: int | str
    name: str

    class Config:
        arbitrary_types_allowed = True


class CredExOut(BaseModel):
    id: int


class BaseOrderReq(BaseModel):
    ad_id: int | str

    asset_amount: float | None = None
    fiat_amount: float | None = None

    # todo: mv from to base to special ex class
    amount_is_fiat: bool = True
    is_sell: bool = None
    cur_exid: int | str = None
    coin_exid: int | str = None
    coin_scale: int = None

    @model_validator(mode="after")
    def check_a_or_b(self):
        if self.amount_is_fiat and not self.fiat_amount:
            raise ValueError("fiat_amount is required if amount_is_fiat")
        if not self.amount_is_fiat and not self.asset_amount:
            raise ValueError("asset_amount is required if not amount_is_fiat")
        if not self.asset_amount and not self.fiat_amount:
            raise ValueError("either fiat_amount or asset_amount is required")
        return self


class BaseOrderPaidReq(BaseModel):
    ad_id: int | str

    cred_id: int | None = None
    pm_id: int | None = None  # or pmcur_id?

    @model_validator(mode="after")
    def check_a_or_b(self):
        if not self.cred_id and not self.pm_id:
            raise ValueError("either cred_id or pm_id is required")
        return self


class BaseAdUpdate(BaseModel):
    id: int | str


class BaseCad(BaseAdUpdate):
    id: str
    createDate: str
    currencyId: str
    maxAmount: str
    minAmount: str
    nickName: str
    paymentPeriod: int
    payments: list[str]
    premium: str
    price: str
    priceType: Literal[0, 1]  # 0 - fix rate, 1 - floating
    quantity: str
    recentOrderNum: int
    remark: str
    side: Literal[0, 1]  # 0 - покупка, 1 - продажа
    tokenId: str
    userId: str
