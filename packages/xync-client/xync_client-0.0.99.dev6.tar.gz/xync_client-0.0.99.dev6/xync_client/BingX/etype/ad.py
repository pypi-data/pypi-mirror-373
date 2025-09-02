from pydantic import BaseModel
from typing import List
from xync_schema.xtype import BaseAd


class UserPaymentMethod(BaseModel):
    id: int
    paymentMethodId: int
    paymentMethodName: str
    paymentMethodIcon: str
    mainColor: str


class PaymentMethod(BaseModel):
    id: int
    name: str
    icon: str
    mainColor: str
    userPaymentMethodList: List[UserPaymentMethod]


class Ad(BaseAd):
    orderNo: str
    tradeRecent: int
    type: int
    asset: str
    fiat: str
    fiatSymbol: str
    totalNumber: float
    availableAmount: float
    priceType: int
    fixPrice: float
    floatRatio: float
    price: float
    minAmount: float
    maxAmount: float
    assetPrecision: int
    fiatPrecision: int
    pricePrecision: int
    paymentMethodList: List[PaymentMethod]
    termsDesc: str
    hidePaymentInfo: int
    nickName: str
    merchantUid: str
    restStatus: int
    onlineStatus: bool
    merchantOnlineHint: str
    avatarUrl: str
    tradeNum30: int
    expireMinute: int
    status: int
    autoReplyMsg: str
    formatPrice: str
    formatMinAmount: str
    formatMaxAmount: str
    promotionAdvert: bool
    promotionAdvertOnline: bool
    promotionAdvertEnableChange: bool
    isCanBeSubsidized: bool
    merchantKycType: int
    merchantVerificationType: int
    isUserMatchCondition: bool
    notMatchConditionReason: str
