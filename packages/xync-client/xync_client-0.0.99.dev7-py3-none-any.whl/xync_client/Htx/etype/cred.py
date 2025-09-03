from typing import Literal

from pydantic import BaseModel

field_ids = {
    926496571879587801: "payee",
    926496571879587802: "bank",
    926496571879587803: "sub_bank",
    926496571879587804: "pay_account",
}

field_types = {"payee": "cred__name", "bank": "pm__name", "sub_bank": None, "pay_account": "cred__detail"}


class Cred(BaseModel):
    fieldId: str
    fieldType: Literal["payee", "bank", "sub_bank", "pay_account"]
    value: str | None = None


class Req(BaseModel):
    __root__: list[Cred]


class ModelField(BaseModel):
    fieldId: str
    name: str
    fieldType: str
    index: int
    maxLength: int
    required: bool
    copyable: bool
    remindWord: str
    valueType: str
    value: str | None = None


class Resp(BaseModel):
    id: int
    uid: int
    userName: str
    bankType: int
    bankNumber: str
    bankName: str
    bankAddress: str | None = None
    qrCode: str | None = None
    isShow: int
    buyingEnable: bool
    sellingEnable: bool
    disabledCurrencyList: list[int]
    modelFields: str | None = ""
    modelFieldsList: list[ModelField]
    color: str
    payMethodName: str
