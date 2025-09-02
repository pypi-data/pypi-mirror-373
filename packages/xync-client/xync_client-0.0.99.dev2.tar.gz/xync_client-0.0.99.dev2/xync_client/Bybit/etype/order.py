from datetime import datetime
from enum import IntEnum
from typing import Literal

from pydantic import BaseModel

from xync_client.Bybit.etype.cred import CredEpyd


class Topic(IntEnum):
    OTC_USER_CHAT_MSG = 1
    OTC_ORDER_STATUS_V2 = 2
    OTC_ORDER_STATUS = 3
    SELLER_CANCEL_CHANGE = 4


class Status(IntEnum):
    deleted = 40  # order canceled
    # created = 10  # waiting for buyer to pay
    appealable = 20  # waiting for seller to release
    canceled = 40
    completed = 50  # order finished
    appealed_by_buyer = 30  # appealing
    appealed_by_seller = 30
    buyer_appeal_disputed_by_seller = 30
    paid = 50
    rejected = 40
    request_canceled = 40
    requested = 10
    seller_appeal_disputed_by_buyer = 30


class StatusApi(IntEnum):
    created = 1
    wait_for_buyer = 10  # ws_canceled
    wait_for_seller = 20
    appealed = 30
    canceled = 40
    completed = 50


class OrderRequest(BaseModel):
    class Side(IntEnum):
        BUY = 0
        SALE = 1

    itemId: str
    tokenId: str
    currencyId: str
    side: Literal["0", "1"]  # 0 покупка, # 1 продажа
    curPrice: str
    quantity: str
    amount: str
    flag: Literal["amount", "quantity"]
    version: str = "1.0"
    securityRiskToken: str = ""


class PreOrderResp(BaseModel):
    price: str  # float
    curPrice: str
    totalAmount: float
    minAmount: float
    maxAmount: float
    minQuantity: float
    maxQuantity: float
    payments: list[str]  # list[int]
    status: Literal[10, 20]
    paymentTerms: list
    paymentPeriod: Literal[15]
    lastQuantity: float
    lastPrice: float
    isOnline: bool
    lastLogoutTime: datetime
    itemPriceAvailableTime: datetime
    itemPriceValidTime: int  # 45000
    itemType: Literal["ORIGIN"]


class OrderResp(BaseModel):
    orderId: str
    isNeedConfirm: bool
    success: bool
    isBulkOrder: bool
    confirmed: str = None
    delayTime: str


class CancelOrderReq(BaseModel):
    orderId: str
    cancelCode: Literal["cancelReason_transferFailed"] = "cancelReason_transferFailed"
    cancelRemark: str = ""
    voucherPictures: str = ""


class JudgeInfo(BaseModel):
    autoJudgeUnlockTime: str
    dissentResult: str
    preDissent: str
    postDissent: str


class Extension(BaseModel):
    isDelayWithdraw: bool
    delayTime: str
    startTime: str


class AppraiseInfo(BaseModel):
    anonymous: str
    appraiseContent: str
    appraiseId: str
    appraiseType: str
    modifyFlag: str
    updateDate: str


class PaymentConfigVo(BaseModel):
    paymentType: str
    checkType: int
    sort: int
    paymentName: str
    addTips: str
    itemTips: str
    online: int
    items: list[dict[str, str | bool]]


class PaymentTerm(BaseModel):
    id: str
    realName: str
    paymentType: int
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
    paymentConfigVo: PaymentConfigVo
    ruPaymentPrompt: bool


class OrderItem(BaseModel):
    id: str
    side: Literal[0, 1]  # int: 0 покупка, 1 продажа (именно для меня - апи агента, и пох мейкер я или тейкер)
    tokenId: str
    orderType: Literal[
        "ORIGIN", "SMALL_COIN", "WEB3"
    ]  # str: ORIGIN: normal p2p order, SMALL_COIN: HotSwap p2p order, WEB3: web3 p2p order
    amount: str
    currencyId: str
    price: str
    notifyTokenQuantity: str
    notifyTokenId: str
    fee: str
    targetNickName: str
    targetUserId: str  # не я
    status: Literal[
        5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110
    ]  # 5: waiting for chain (only web3), 10: waiting for buyer to pay, 20: waiting for seller to release, 30: appealing, 40: order cancelled, 50: order finished, 60: paying (only when paying online), 70: pay fail (only when paying online), 80: exception cancelled (the coin convert to other coin, only hotswap), 90: waiting for buyer to select tokenId, 100: objectioning, 110: waiting for the user to raise an objection
    selfUnreadMsgCount: str
    createDate: str
    transferLastSeconds: str
    appealLastSeconds: str
    userId: str  # я
    sellerRealName: str
    buyerRealName: str
    judgeInfo: JudgeInfo
    unreadMsgCount: str
    extension: Extension
    bulkOrderFlag: bool


class OrderFull(OrderItem):
    itemId: str
    makerUserId: str
    targetAccountId: str
    targetFirstName: str
    targetSecondName: str
    targetUserAuthStatus: int
    targetConnectInformation: str
    payerRealName: str
    tokenName: str
    quantity: str
    payCode: str
    paymentType: int
    transferDate: str
    paymentTermList: list[CredEpyd]
    remark: str
    recentOrderNum: int
    recentExecuteRate: int
    appealContent: str
    appealType: int
    appealNickName: str
    canAppeal: str
    totalAppealTimes: str
    paymentTermResult: CredEpyd
    confirmedPayTerm: CredEpyd
    appealedTimes: str
    orderFinishMinute: int
    makerFee: str
    takerFee: str
    showContact: bool
    contactInfo: list[str]
    tokenBalance: str
    fiatBalance: str
    updateDate: str
    judgeType: str
    canReport: bool
    canReportDisagree: bool
    canReportType: list[str]
    canReportDisagreeType: list[str]
    appraiseStatus: str
    appraiseInfo: AppraiseInfo
    canReportDisagreeTypes: list[str]
    canReportTypes: list[str]
    middleToken: str
    beforePrice: str
    beforeQuantity: str
    beforeToken: str
    alternative: str
    appealUserId: str
    cancelResponsible: str
    chainType: str
    chainAddress: str
    tradeHashCode: str
    estimatedGasFee: str
    gasFeeTokenId: str
    tradingFeeTokenId: str
    onChainInfo: str
    transactionId: str
    displayRefund: str
    chainWithdrawLastSeconds: str
    chainTransferLastSeconds: str
    orderSource: str
    cancelReason: str
    sellerCancelExamineRemainTime: str
    needSellerExamineCancel: bool
    couponCurrencyAmount: str
    totalCurrencyAmount: str
    usedCoupon: bool  # bool: 1: used, 2: no used
    couponTokenId: str
    couponQuantity: str
    completedOrderAppealCount: int
    totalCompletedOrderAppealCount: int
    realOrderStatus: int
    appealVersion: int
    helpType: str
    appealFlowStatus: str
    appealSubStatus: str
    targetUserType: str
    targetUserDisplays: list[str]
    appealProcessChangeFlag: bool
    appealNegotiationNode: int


class Message(BaseModel):
    id: str
    accountId: str
    message: str
    msgType: Literal[
        0, 1, 2, 5, 6, 7, 8
    ]  # int: 0: system message, 1: text (user), 2: image (user), 5: text (admin), 6: image (admin), 7: pdf (user), 8: video (user)
    msgCode: int
    createDate: str
    isRead: Literal[0, 1]  # int: 1: read, 0: unread
    contentType: Literal["str", "pic", "pdf", "video"]
    roleType: str
    userId: str
    orderId: str
    msgUuid: str
    nickName: str
    read: Literal[0, 1]
    fileName: str
    onlyForCustomer: int


class _BaseChange(BaseModel):
    userId: int
    makerUserId: int
    id: str
    status: StatusApi
    createDate: int
    side: int
    appealedTimes: int
    totalAppealedTimes: int


class StatusChange(_BaseChange):
    appealVersion: int = None


class CountDown(_BaseChange):
    cancelType: Literal["ACTIVE", "TIMEOUT", ""]


class _BaseMsg(BaseModel):
    userId: int
    orderId: str
    message: str = None
    msgUuid: str
    msgUuId: str
    createDate: str
    contentType: str
    roleType: Literal["user", "sys", "alarm"]


class Receive(_BaseMsg):
    id: int
    msgCode: int
    onlyForCustomer: int


class Read(_BaseMsg):
    readAmount: int
    read: Literal["111", "101"]
    orderStatus: StatusApi


class SellerCancelChange(BaseModel):
    userId: int
    makerUserId: int
    id: str
    createDate: int
