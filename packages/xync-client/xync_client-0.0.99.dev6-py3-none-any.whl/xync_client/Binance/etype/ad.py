from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from xync_schema.xtype import BaseAd


class TradeMethod(BaseModel):
    iconUrlColor: Optional[str] = None
    identifier: str
    payAccount: Optional[str] = None
    payBank: Optional[str] = None
    payId: Optional[str] = None
    payMethodId: str
    paySubBank: Optional[str] = None
    payType: str
    tradeMethodBgColor: str
    tradeMethodName: str
    tradeMethodShortName: Optional[str] = None


class Adv(BaseModel):
    abnormalStatusList: Optional[List[str]] = None
    adAdditionalKycVerifyItems: Optional[List[Any]] = None
    adTradeInstructionTagInfoRets: Optional[List[Any]] = None
    advNo: str
    advStatus: Optional[str] = None
    advUpdateTime: Optional[str] = None
    advVisibleRet: Optional[Dict[str, Any]] = None
    allowTradeMerchant: Optional[bool] = None
    amountAfterEditing: Optional[str] = None
    asset: str
    assetLogo: Optional[str] = None
    assetScale: int
    assetVo: Optional[Dict[str, Any]] = None
    autoReplyMsg: Optional[str] = None
    buyerBtcPositionLimit: Optional[str] = None
    buyerKycLimit: Optional[str] = None
    buyerRegDaysLimit: Optional[str] = None
    classify: str
    closeReason: Optional[str] = None
    commissionRate: str
    createTime: Optional[str] = None
    currencyRate: Optional[str] = None
    dynamicMaxSingleTransAmount: str
    dynamicMaxSingleTransQuantity: str
    fiatScale: int
    fiatSymbol: str
    fiatUnit: str
    fiatVo: Optional[Dict[str, Any]] = None
    initAmount: Optional[str] = None
    inventoryType: Optional[str] = None
    invisibleReason: Optional[str] = None
    invisibleType: Optional[str] = None
    isSafePayment: bool
    isTradable: bool
    launchCountry: Optional[List[str]] = None
    maxSingleTransAmount: str
    maxSingleTransQuantity: str
    minFiatAmountForAdditionalKyc: Optional[str] = None
    minSingleTransAmount: str
    minSingleTransQuantity: str
    minTakerFee: Optional[str] = None
    nonTradableRegions: Optional[List[str]] = None
    offlineReason: Optional[str] = None
    payTimeLimit: int
    price: str
    priceFloatingRatio: Optional[str] = None
    priceScale: int
    priceType: Optional[str] = None
    rateFloatingRatio: Optional[str] = None
    remarks: Optional[str] = None
    storeInformation: Optional[Dict[str, Any]] = None
    surplusAmount: str
    takerAdditionalKycRequired: int
    takerCommissionRate: Optional[str] = None
    tradableQuantity: str
    tradeMethodCommissionRates: Optional[List[Any]] = None
    tradeMethods: List[TradeMethod]
    tradeType: str
    userAllTradeCountMax: Optional[str] = None
    userAllTradeCountMin: Optional[str] = None
    userBuyTradeCountMax: Optional[str] = None
    userBuyTradeCountMin: Optional[str] = None
    userSellTradeCountMax: Optional[str] = None
    userSellTradeCountMin: Optional[str] = None
    userTradeCompleteCountMin: Optional[str] = None
    userTradeCompleteRateFilterTime: Optional[str] = None
    userTradeCompleteRateMin: Optional[str] = None
    userTradeCountFilterTime: Optional[str] = None
    userTradeType: Optional[str] = None
    userTradeVolumeAsset: Optional[str] = None
    userTradeVolumeFilterTime: Optional[str] = None
    userTradeVolumeMax: Optional[str] = None
    userTradeVolumeMin: Optional[str] = None


class Advertiser(BaseModel):
    activeTimeInSecond: int
    advConfirmTime: Optional[str] = None
    badges: Optional[List[str]] = None
    email: Optional[str] = None
    isBlocked: bool
    margin: Optional[str] = None
    marginUnit: Optional[str] = None
    mobile: Optional[str] = None
    monthFinishRate: float
    monthOrderCount: int
    nickName: str
    orderCount: Optional[int] = None
    positiveRate: float
    proMerchant: Optional[Dict[str, Any]] = None
    realName: Optional[str] = None
    registrationTime: Optional[str] = None
    tagIconUrls: List[str]
    userGrade: int
    userIdentity: str
    userNo: str
    userType: str
    vipLevel: Optional[int] = None


class Ad(BaseAd):
    adv: Adv
    advertiser: Advertiser
    privilegeDesc: Optional[str] = None
    privilegeType: int | None = None
