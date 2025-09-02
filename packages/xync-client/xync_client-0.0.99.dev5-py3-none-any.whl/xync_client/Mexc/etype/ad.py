from pydantic import BaseModel, Field
from xync_schema.xtype import BaseAd
from typing import Optional


class Merchant(BaseModel):
    nickName: str
    imId: str
    memberId: str
    registry: int  # timestamp in milliseconds
    vipLevel: int
    greenDiamond: bool
    emailAuthentication: bool
    smsAuthentication: bool
    identityVerification: bool
    lastOnlineTime: int  # timestamp in milliseconds
    badge: str
    merchantType: str


class MerchantStatistics(BaseModel):
    totalBuyCount: int
    totalSellCount: int
    doneLastMonthCount: int
    goodRate: Optional[str] = None
    lastMonthCompleteRate: str  # decimal as string
    completeRate: str  # decimal as string
    avgHandleTime: float
    avgBuyHandleTime: float
    avgSellHandleTime: float


class Ad(BaseAd):
    exid: str | None = Field(alias="id")
    price: float
    availableQuantity: float
    coinName: str
    countryCode: str
    updateTime: int  # timestamp in milliseconds
    currency: str
    tradeType: int
    payMethod: str
    merchant: Merchant
    merchantStatistics: MerchantStatistics
    expirationTime: int  # in minutes?
    autoResponse: str
    tradeTerms: str
    minTradeLimit: float
    maxTradeLimit: float
    kycLevel: int
    requireMobile: bool
    fiatCount: int
    fiatCountLess: int
    maxPayLimit: int
    orderPayCount: int
    exchangeCount: int
    minRegisterDate: int
    blockTrade: bool
    tags: str
