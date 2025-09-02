from enum import StrEnum
from typing import List, Optional, Any, Literal
from pydantic import BaseModel, Field, field_serializer
from xync_schema import xtype
from xync_schema.xtype import BaseAd

from xync_client.Abc.xtype import BaseAdUpdate


class AdStatus(StrEnum):
    sold_out = "1"
    active = "2"


class AdsReq(BaseModel):
    tokenId: str
    currencyId: str
    side: Literal["0", "1"]  # 0 покупка, # 1 продажа


class Currency(BaseModel):
    currencyId: str
    exchangeId: str
    id: str
    orgId: str
    scale: int


class Token(BaseModel):
    exchangeId: str
    id: str
    orgId: str
    scale: int
    sequence: int
    tokenId: str


class SymbolInfo(BaseModel):
    buyAd: Optional[Any]
    buyFeeRate: str
    currency: Currency
    currencyId: str
    currencyLowerMaxQuote: str
    currencyMaxQuote: str
    currencyMinQuote: str
    exchangeId: str
    id: str
    itemDownRange: str
    itemSideLimit: int
    itemUpRange: str
    kycCurrencyLimit: str
    lowerLimitAlarm: int
    orderAutoCancelMinute: int
    orderFinishMinute: int
    orgId: str
    sellAd: Optional[Any]
    sellFeeRate: str
    status: int
    token: Token
    tokenId: str
    tokenMaxQuote: str
    tokenMinQuote: str
    tradeSide: int
    upperLimitAlarm: int


class TradingPreferenceSet(BaseModel):
    completeRateDay30: str
    hasCompleteRateDay30: int
    hasNationalLimit: int
    hasOrderFinishNumberDay30: int
    hasRegisterTime: int
    hasUnPostAd: int
    isEmail: int
    isKyc: int
    isMobile: int
    nationalLimit: str
    orderFinishNumberDay30: int
    registerTimeThreshold: int


class Ad(BaseAd):
    accountId: str = None  # for initial actualize
    authStatus: int = None  # for initial actualize
    authTag: List[str] = None  # for initial actualize
    ban: bool = None  # for initial actualize
    baned: bool = None  # for initial actualize
    blocked: str = None  # for initial actualize
    createDate: str = None  # for initial actualize
    currencyId: str = None  # for initial actualize
    executedQuantity: str = None  # for initial actualize
    fee: str = None  # for initial actualize
    finishNum: int = None  # for initial actualize
    frozenQuantity: str = None  # for initial actualize
    id: str = Field(serialization_alias="exid")
    isOnline: bool = None  # for initial actualize
    itemType: str = None  # for initial actualize
    lastLogoutTime: str = None  # for initial actualize
    lastQuantity: str = Field(serialization_alias="quantity")
    makerContact: bool = None  # for initial actualize
    maxAmount: str = Field(serialization_alias="max_fiat")
    minAmount: str = Field(serialization_alias="min_fiat")
    nickName: str = None  # for initial actualize
    orderNum: int = None  # for initial actualize
    paymentPeriod: int = None  # for initial actualize
    payments: List[str] = None  # for initial actualize
    premium: str = None  # for initial actualize
    price: str = None  # for initial actualize
    priceType: Literal[0, 1] = None  # for initial actualize  # 0 - fix rate, 1 - floating
    quantity: str = Field(serialization_alias="allQuantity")  # for initial actualize
    recentExecuteRate: int = None  # for initial actualize
    recentOrderNum: int = None  # for initial actualize
    recommend: bool = None  # for initial actualize
    recommendTag: str = None  # for initial actualize
    remark: str = Field(serialization_alias="auto_msg")
    side: Literal[0, 1] = None  # for initial actualize  # 0 - покупка, 1 - продажа (для мейкера, т.е КАКАЯ объява)
    status: Literal[10, 20, 30]  # 10: online; 20: offline; 30: completed
    symbolInfo: SymbolInfo = None  # for initial actualize
    tokenId: str = None  # for initial actualize
    tokenName: str = None  # for initial actualize
    tradingPreferenceSet: TradingPreferenceSet | None = None  # for initial actualize
    userId: str
    userMaskId: str = None  # for initial actualize
    userType: str = None  # for initial actualize
    verificationOrderAmount: str = None  # for initial actualize
    verificationOrderLabels: List[Any] = None  # for initial actualize
    verificationOrderSwitch: bool = None  # for initial actualize
    version: int = None  # for initial actualize
    #
    #
    # class Ad(BaseAd):
    #     accountId: str = None  # for initial actualize
    #     authStatus: int = None  # for initial actualize
    #     authTag: List[str] = None  # for initial actualize
    #     ban: bool = None  # for initial actualize
    #     baned: bool = None  # for initial actualize
    #     blocked: str = None  # for initial actualize
    #     createDate: str = None  # for initial actualize
    #     currencyId: str = None  # for initial actualize
    #     executedQuantity: str = None  # for initial actualize
    #     fee: str = None  # for initial actualize
    #     finishNum: int = None  # for initial actualize
    #     frozenQuantity: str = None  # for initial actualize
    #     exid: str = Field(serialization_alias="id")
    #     isOnline: bool = None  # for initial actualize
    #     itemType: str = None  # for initial actualize
    #     lastLogoutTime: str = None  # for initial actualize
    #     quantity: str = Field(serialization_alias="lastQuantity")
    #     makerContact: bool = None  # for initial actualize
    #     max_fiat: str = Field(serialization_alias="maxAmount")
    #     min_fiat: str = Field(serialization_alias="minAmount")
    #     nickName: str = None  # for initial actualize
    #     orderNum: int = None  # for initial actualize
    #     paymentPeriod: int = None  # for initial actualize
    #     payments: List[str] = None  # for initial actualize
    #     premium: str = None  # for initial actualize
    #     price: str = None  # for initial actualize
    #     priceType: Literal[0, 1] = None  # for initial actualize  # 0 - fix rate, 1 - floating
    #     allQuantity: str = Field(serialization_alias="quantity")  # for initial actualize
    #     recentExecuteRate: int = None  # for initial actualize
    #     recentOrderNum: int = None  # for initial actualize
    #     recommend: bool = None  # for initial actualize
    #     recommendTag: str = None  # for initial actualize
    #     auto_msg: str = Field(serialization_alias="remark")
    #     is_sell: Literal[0, 1] = Field(serialization_alias="side")  # for initial actualize # 0 - покупка, 1 - продажа (для мейкера, т.е КАКАЯ объява)
    #     status: Literal[10, 20, 30]  # 10: online; 20: offline; 30: completed
    #     symbolInfo: SymbolInfo = None  # for initial actualize
    #     tokenId: str = None  # for initial actualize
    #     tokenName: str = None  # for initial actualize
    #     tradingPreferenceSet: TradingPreferenceSet | None = None  # for initial actualize
    #     userId: str = Field(serialization_alias="maker__exid")
    #     userMaskId: str = None  # for initial actualize
    #     userType: str = None  # for initial actualize
    #     verificationOrderAmount: str = None  # for initial actualize
    #     verificationOrderLabels: List[Any] = None  # for initial actualize
    #     verificationOrderSwitch: bool = None  # for initial actualize
    #     version: int = None  # for initial actualize

    @field_serializer("status")
    def status(self, status, _info) -> xtype.AdStatus:
        return {10: xtype.AdStatus.active, 20: xtype.AdStatus.defActive, 30: xtype.AdStatus.soldOut}[status]


class AdPostRequest(BaseModel):
    tokenId: str
    currencyId: str
    side: Literal[0, 1]  # 0 - покупка, 1 - продажа
    priceType: Literal[0, 1]  # 0 - fix rate, 1 - floating
    premium: str
    price: str
    minAmount: str
    maxAmount: str
    remark: str
    tradingPreferenceSet: TradingPreferenceSet
    paymentIds: list[str]
    quantity: str
    paymentPeriod: int
    itemType: str


class AdUpdateRequest(AdPostRequest, BaseAdUpdate):
    actionType: Literal["MODIFY", "ACTIVE"] = "MODIFY"
