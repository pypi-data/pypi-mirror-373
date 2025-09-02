from pydantic import BaseModel, Field
from typing import List, Optional
from xync_schema.xtype import BaseAd


class AdPayType(BaseModel):
    id: str
    bankName: Optional[str] = None
    payTypeCode: str
    payQrcodePic: Optional[str] = None
    payTypeNumber: Optional[str] = None
    subBranch: Optional[str] = None
    reservedFields: Optional[str] = None


class Ad(BaseAd):
    exid: str = Field(validation_alias="id")
    side: str
    legal: str
    currency: str
    currencyQuantity: str
    currencyBalanceQuantity: str
    premium: str
    status: str
    limitPrice: Optional[str] = None
    floatPrice: str
    limitMinQuote: str
    limitMaxQuote: str
    adPayTypes: List[AdPayType]
    remarks: str
    needKyc: str
    nickName: str
    showLetter: str
    lastActiveTime: int
    lastActiveDesc: str
    lastActiveStatus: str
    priceType: str
    portraitURL: Optional[str] = None
    displayStatus: str
    kycLevel: int
    tradeTimeLimit: int
    updatedAt: int
    goldMerchants: int
    foxKingMerchants: int
    adTarget: int
    dealOrderNum: str
    dealOrderRate: str
    userId: str
    tradeLimitTip: Optional[str] = None
    opponentBalanceLimit: str
    blackStatus: int
    self: bool
