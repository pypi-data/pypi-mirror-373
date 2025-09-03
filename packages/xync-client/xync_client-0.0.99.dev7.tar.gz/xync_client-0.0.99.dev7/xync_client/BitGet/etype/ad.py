from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field
from xync_schema.xtype import BaseAd


class PaymethodDetail(BaseModel):
    name: str
    required: int
    type: str


class PaymethodInfo(BaseModel):
    colorValue: str
    iconUrl: str
    isModifyKyc: int
    paymethodId: str
    paymethodInfo: List[PaymethodDetail]
    paymethodName: str
    paymethodNameHandle: bool


class Ad(BaseAd):
    exid: int | str | None = Field(alias="adNo")
    adEditorTime: str
    # adNo: str
    adType: int
    advImages: List[str]
    advertiseIsEvent: int
    allowMerchantPlace: int
    allowPlace: int
    amount: str
    avgTime: int
    businessCertifiedList: List
    businessCertifiedResp: dict | None
    cancellPlaceOrderTime: int
    certifiedMerchant: int
    coinCode: str
    coinPrecision: int
    countryList: List
    createTime: datetime
    customizeState: int
    delAdv: int
    editAmount: float
    encryptUserId: str
    fiatCode: str
    fiatPrecision: int
    fiatSymbol: str
    floatValue: str
    fundState: bool
    goodEvaluationRate: int
    headColor: str
    hideFlag: int
    iconUrl: str
    lastAmount: float
    limitPrice: float
    maxAmount: float
    maxCompleteDefault: int
    minAmount: float
    minCompleteDefault: int
    nickName: str
    orderMode: Literal["close"]
    payDuration: int
    paymethodInfo: List[PaymethodInfo]
    positionNum: str
    price: float
    priceType: int
    priceValue: float
    recentOnlineText: str
    showOnline: bool
    soldAmount: float
    state: int
    taxAmount: float
    thirtyCompletionRate: float = None
    thirtyTunoverNum: float = None
    transactionTermsRespList: List
    turnoverNum: float
    turnoverRate: float = None
    turnoverRateNum: float  # Changed from int to float
    userId: str
