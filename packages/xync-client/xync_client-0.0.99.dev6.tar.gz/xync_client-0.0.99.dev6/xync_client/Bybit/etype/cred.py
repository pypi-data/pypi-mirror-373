from typing import Literal

from pydantic import BaseModel

from xync_client.Abc.xtype import CredExOut


class PaymentItem(BaseModel):
    view: bool
    name: str
    label: str
    placeholder: str
    type: str
    maxLength: str
    required: bool


class PaymentConfigVo(BaseModel):
    paymentType: str
    checkType: int
    sort: int
    paymentName: str
    addTips: str
    itemTips: str
    online: Literal[0, 1]  # Non-balance coin purchase (0 Offline), balance coin purchase (1 Online)
    items: list[PaymentItem]


class CredEpyd(CredExOut):
    id: str  # int
    realName: str
    paymentType: int  # int
    bankName: str
    branchName: str
    accountNo: str
    qrcode: str
    visible: int
    payMessage: str
    firstName: str
    lastName: str
    secondLastName: str
    clabe: str
    debitCardNumber: str
    mobile: str
    businessName: str
    concept: str
    online: str
    paymentExt1: str
    paymentExt2: str
    paymentExt3: str
    paymentExt4: str
    paymentExt5: str
    paymentExt6: str
    paymentTemplateVersion: int


class MyCredEpyd(CredEpyd):  # todo: заменить везде где надо CredEpyd -> MyCredEpyd
    countNo: str
    hasPaymentTemplateChanged: bool
    paymentConfigVo: PaymentConfigVo  # only for my cred
    realNameVerified: bool
    channel: str
    currencyBalance: list[str]
