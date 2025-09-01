from typing import Literal

from pydantic import BaseModel
from xync_schema.xtype import BaseAd


class TradeRule(BaseModel):
    title: str
    titleValue: str
    content: str
    inputType: int
    inputValue: str
    hint: str
    contentCode: str
    sort: int


class Req(BaseModel):
    tradeType: int
    coinId: int
    currency: int
    minTradeLimit: float
    maxTradeLimit: float
    tradeCount: float
    password: str
    payTerm: int
    isFixed: Literal["off", "on"]
    premium: int
    isAutoReply: Literal["off", "on"]
    takerAcceptOrder: int
    isPayCode: Literal["off", "on"]
    isVerifyCapital: bool
    receiveAccounts: int
    deviation: int
    isTakerLimit: Literal["off", "on"]
    blockType: int
    session: int
    chargeType: bool
    apiVersion: int
    channel: str
    tradeRulesV2: list[TradeRule]
    securityToken: str | None = ""
    fixedPrice: str | None = ""
    autoReplyContent: str | None = ""
    tradeRule: str | None = ""


class PayMethod(BaseModel):
    payMethodId: int
    name: str
    color: str | None = None
    isRecommend: bool | None = None


class PayName(BaseModel):
    bankType: int
    id: int


class Resp(BaseAd):
    blockType: int
    chargeType: bool
    coinId: int
    currency: int
    gmtSort: int
    id: int
    isCopyBlock: bool
    isFollowed: bool
    isOnline: bool
    isTrade: bool
    isVerifyCapital: bool
    maxTradeLimit: str
    merchantLevel: int
    minTradeLimit: str
    orderCompleteRate: str
    payMethod: str
    payMethods: list[PayMethod]
    payName: str  # list[PayName]  # приходит массив объектов внутри строки
    payTerm: int
    price: str
    takerAcceptAmount: str
    takerAcceptOrder: int
    takerLimit: int
    thumbUp: int
    totalTradeOrderCount: int
    tradeCount: str
    tradeMonthTimes: int
    tradeType: int
    uid: int
    userName: str
    merchantTags: list[int] | None
    labelName: str | None = None
    seaViewRoom: str | None = None
