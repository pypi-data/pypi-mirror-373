from pydantic import BaseModel
from typing import List, Optional
from xync_schema.xtype import BaseAd


class PromoBadgeInfoVo(BaseModel):
    badgeList: List[str]


class LegacyMerchantInfo(BaseModel):
    accountAssociationDate: int
    avgPaidTime: int
    avgReleasedTime: int
    cancelledOrderQuantity: int
    completedOrderQuantity: int
    hasLegacyMerchant: bool
    legacyMerchantRegisteredDate: int
    nickname: str
    totalCompletionRate: str


class MerchantInfo30DayOrderInfo(BaseModel):
    completedBuyOrderQuantity30Day: int
    completedOrderQuantity30Day: int
    completedSellOrderQuantity30Day: int
    completionRateBuyOrderQuantity30Day: float
    completionRateOrderQuantity30Day: float
    completionRateSellOrderQuantity30Day: float
    servedUsersCompletedOrders30Day: int


class MerchantScoreInfo(BaseModel):
    merchantScore: int
    scorePercentileRank: int
    showMerchantScoreInfo: bool


class UserActiveStatusVo(BaseModel):
    userActiveStatus: int
    userActiveStatusText: str


class VideoVerificationStatus(BaseModel):
    failedReason: str
    status: int


class Ads(BaseAd):
    alreadyTraded: bool
    availableAmount: str
    avgCompletedTime: int
    avgPaymentTime: int
    baseCurrency: str
    black: bool
    cancelledOrderQuantity: int
    completedOrderQuantity: int
    completedRate: str
    creatorType: str
    guideUpgradeKyc: bool
    id: str
    intention: bool
    isInstitution: int
    maxCompletedOrderQuantity: int
    maxUserCreatedDate: int
    merchantId: str
    minCompletedOrderQuantity: int
    minCompletionRate: str
    minKycLevel: int
    minSellOrderQuantity: int
    minSellOrders: int
    minTradeVolume: int
    mine: bool
    nickName: str
    paymentMethods: List[str]
    paymentTimeoutMinutes: int
    posReviewPercentage: str
    price: str
    promoBadgeInfoVo: PromoBadgeInfoVo
    publicUserId: str
    quoteCurrency: str
    quoteMaxAmountPerOrder: str
    quoteMinAmountPerOrder: str
    quoteScale: int
    quoteSymbol: str
    receivingAds: bool
    safetyLimit: bool
    side: str
    userActiveStatusVo: None
    userType: str
    verificationType: int
    whitelistedCountries: List[str]


class Ad(BaseAd):
    allowChat: bool
    auditState: int
    avatarImage: str
    avgCompletedTime: str
    avgPaidTime: str
    blackState: str
    blackUserCount: Optional[str] = None
    businessHoursInfo: Optional[str] = None
    canCurrentUserViewOrderReview: bool
    commonOrderTotal: Optional[str] = None
    completedBuyOrderQuantity: int
    completedOrderQuantity: int
    completedSellOrderQuantity: int
    countryIcon: str
    countryId: str
    countryName: str
    createdDate: int
    description: str
    disabled: bool
    emailVerified: bool
    finishRate: str
    follow: bool
    followerCount: int
    fundsInfo: Optional[str] = None
    isInstitution: int
    kycDate: int
    kycLevel: str
    kycRedirect: int
    kycVerified: bool
    legacyMerchantInfo: LegacyMerchantInfo
    merchantDeposit: int
    merchantDepositCurrency: str
    merchantInfo30DayOrderInfo: MerchantInfo30DayOrderInfo
    merchantRegistrationDate: int
    merchantScoreInfo: MerchantScoreInfo
    negativeReviewNum: int
    nickName: str
    orderTotalCount: str
    phoneVerified: bool
    positiveReviewNum: int
    positiveReviewPercentage: int
    promoBadgeInfoVo: PromoBadgeInfoVo
    publicMerchantId: Optional[str] = None
    publicUserId: str
    realName: str
    self: bool
    showAddNicknameButton: bool
    showAddNicknameTooltip: bool
    showReview: bool
    showingVideoVerification: bool
    totalReviewNum: int
    tradeUserCount: str
    userActiveStatusVo: UserActiveStatusVo
    userType: str
    videoVerificationStatus: VideoVerificationStatus
    vip: bool
