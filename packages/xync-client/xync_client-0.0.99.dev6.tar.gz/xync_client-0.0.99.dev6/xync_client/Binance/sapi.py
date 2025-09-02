import hashlib
import hmac
from enum import StrEnum

from xync_schema import models
from xync_schema.enums import TradeType
from xync_schema.models import Pm, Coin, Cur, Pair, Ad
from asyncio import run
from x_client.aiohttp import Client
from x_model import init_db

from xync_client.loader import BKEY, BSEC, PG_DSN
from requests import get


class Ep(StrEnum):
    GET_AD = "/sapi/v1/c2c/ads/getDetailByNo"  # 2
    GET_REF_PRICE = "/sapi/v1/c2c/ads/getReferencePrice"  # 3
    GET_MY_ADS = "/sapi/v1/c2c/ads/listWithPagination"  # 4
    POST_AD = "/sapi/v1/c2c/ads/post"  # 5
    GET_PMS = "/sapi/v1/c2c/paymentMethod/listAll"  # 37
    GET_CHAT = "/sapi/v1/c2c/chat/retrieveChatMessagesWithPagination"  # 43


class Sapi(Client):
    def __init__(self, key: str, secret: str):
        self.key = key
        self.secret = secret
        self.headers = {"X-MBX-APIKEY": key}
        super().__init__("api-gcp.binance.com")

    def __sign(self, params: dict):
        ts = get("https://api-gcp.binance.com/api/v3/time").json()["serverTime"]
        params = {**(params or {}), "timestamp": ts}
        """Makes a signature and adds it to the params dictionary."""
        query: str = "&".join(f"{k}={v}" for k, v in params.items())
        m = hmac.new(self.secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256)
        return {**params, "signature": m.hexdigest()}

    async def _get(self, endpoint: str, params: dict = None, data_key: str = "data"):
        resp = await super()._get(endpoint, self.__sign(params), data_key)
        return resp

    async def _post(self, endpoint: str, data: dict = None, params: dict = None, data_key: str = None):
        resp = await super()._post(endpoint, data, self.__sign(params), data_key)
        return resp

    """ PUBLIC METHS """

    # 2: Get details of a specific advertisement
    async def get_ad(self, ad_num: int):
        return await self._post(Ep.GET_AD, {"adsNo": ad_num})

    # 3
    async def get_ref_price(self, assets: [Coin], fiat: Cur, tt: TradeType):
        body = {
            "assets": [a.ticker for a in assets],  # len <= 3
            "fiatCurrency": fiat.ticker,
            "fromUserRole": "USER",  # ADVERTISER
            "payType": "BANK",  # WECHAT
            "tradeType": tt.name,
        }
        return await self._post(Ep.GET_REF_PRICE, body)

    # 4
    async def get_my_ads(self, page: int = 1, rows: int = 100):
        body = {
            # "advNo": "string",
            # "advStatus": 0,
            # "asset": "string",
            # "classify": "string",
            # "endDate": "2019-08-24T14:15:22Z", "fiatUnit": "string",
            # "inDeal": 0,
            # "order": "string",
            "page": page,
            "rows": rows,
            # "sort": "string",
            # "startDate": "2019-08-24T14:15:22Z", "tradeType": "string"
        }
        return await self._post(Ep.GET_MY_ADS, body)

    # 5
    async def post_ad(
        self,
        asset: [Coin],
        fiat: Cur,
        tt: TradeType,
        amount: float,
        price: float,
        min_limit: int,
        max_limit: int,
        auto_reply: str = "",
    ):
        body = {
            "asset": asset,
            "authType": "GOOGLE",
            "autoReplyMsg": auto_reply,
            "buyerBtcPositionLimit": 0,
            "buyerKycLimit": 0,
            "buyerRegDaysLimit": 0,
            "classify": "mass",  # profession, block, f2f
            "code": "string",
            # "emailVerifyCode": "string",
            "fiatUnit": fiat,
            "googleVerifyCode": "string",
            "initAmount": amount,
            "maxSingleTransAmount": min_limit,
            "minSingleTransAmount": max_limit,
            # "mobileVerifyCode": "string",
            # "onlineDelayTime": 0,
            # "onlineNow": True,
            "payTimeLimit": (90, 15)[tt],
            "price": price,
            # "priceFloatingRatio": 0,
            "priceType": 1,  # 1: fix, 2: float
            # "rateFloatingRatio": 0,
            "remarks": "string",
            "saveAsTemplate": 0,
            # "templateName": "string",
            "tradeMethods": [{"identifier": "string", "payId": 0, "payType": "string"}],
            "tradeType": tt.name,
            # "userAllTradeCountMax": 0,
            # "userAllTradeCountMin": 0,
            # "userBuyTradeCountMax": 0,
            # "userBuyTradeCountMin": 0,
            # "userSellTradeCountMax": 0,
            # "userSellTradeCountMin": 0,
            # "userTradeCompleteCountMin": 0,
            # "userTradeCompleteRateFilterTime": 0,
            # "userTradeCompleteRateMin": 0,
            # "userTradeCountFilterTime": 0,
            # "userTradeType": 0,
            # "userTradeVolumeAsset": "string",
            # "userTradeVolumeFilterTime": 0,
            # "userTradeVolumeMax": 0,
            # "userTradeVolumeMin": 0,
            # "yubikeyVerifyCode": "string"
        }
        return await self._post(Ep.POST_AD, body)

    # 6. Search Ad
    async def search_ads(self, asset, fiat, trade_type, pms: [str] = None, amount: int = None, page=1, rows=20):
        """
        Search advertisements based on search criteria.

        Args:
            asset (str): Asset.
            fiat (str): Fiat currency.
            trade_type (str): Trade type ('BUY' or 'SELL').
            pms ([string]): payment types,
            amount (int, optional): payment types,
            page (int, optional): Page number. Defaults to 1.
            rows (int, optional): Number of rows per page. Defaults to 20.

        Returns:
            dict: List of matching advertisements.
        """
        data = {
            "page": page,
            "rows": rows,
            "asset": asset,
            "fiat": fiat,
            "tradeType": trade_type,
            "payTypes": pms,
            # "sort": "asc",
            "transAmount": amount,
        }
        return await self._post("/sapi/v1/c2c/ads/search", data)

    # 7. Update Ad
    async def update_ad(self, adv_no, price):
        """
        Update the price of an advertisement.

        Args:
            adv_no (str): Advertisement number.
            price (str): New price.

        Returns:
            dict: Updated advertisement details.
        """
        return await self._post("/sapi/v1/c2c/ads/update", {"advNo": adv_no, "price": price})

    # 9. Get coins
    async def get_coins(self):
        return await self._post("/sapi/v1/c2c/digitalCurrency/list")

    # 10. Get fiats
    async def get_fiats(self):
        return await self._post("/sapi/v1/c2c/fiatCurrency/list")

    # 22. Get details of a specific order.
    async def get_order_details(self, order_number):
        return await self._post("/sapi/v1/c2c/orderMatch/getUserOrderDetail", {"adOrderNo": order_number})

    # 24. List orders
    async def get_order_list(self, request_body):
        """
        Get a list of orders.

        Args:
            request_body (dict): Request body parameters.

        Returns:
            dict: List of orders.
        """
        return await self._post("/sapi/v1/c2c/orderMatch/listOrders", request_body)

    # 36. Get My Payment Method info by ID
    async def get_my_pay_meth(self, idd):
        return await self._get("/sapi/v1/c2c/paymentMethod/getPayMethodById", {"id": idd})

    # 37. Get available Payment Methods List for current user
    async def get_pay_meths(self):
        return await self._post(Ep.GET_PMS)

    # 38. Get current user info
    async def get_user(self):
        return await self._post("/sapi/v1/c2c/user/baseDetail")

    # 42. Get wss-url, lister key and token
    async def get_chat_creds(self, client_type="web"):
        return await self._get("/sapi/v1/c2c/chat/retrieveChatCredential", {"clientType": client_type})

    # 43. Get chat messages related to a specific order
    async def get_chat(self, order_number, page=1, rows=10):
        return await self._get(Ep.GET_CHAT, params={"page": page, "rows": rows, "orderNo": order_number})


async def main():
    await init_db(PG_DSN, models)  # init db
    sapi = Sapi(BKEY, BSEC)
    pms = await sapi.get_pay_meths()
    await sapi.get_user()

    # coin_ids = [coin.ticker for coin in coins]
    # for chunk in batched(coin_ids, 3):
    #     for cur in await Cur.filter(exs__id__contains=1):
    #         for tt in TradeType:
    #             rp = await sapi.get_ref_price(chunk, cur.ticker, tt)
    #             print(rp)

    # pm = await sapi.get_my_pay_meth(31986806)
    # ads = await sapi.get_my_ads()

    # [await Pm.update_or_create({'name': pm['name'], 'identifier': pm['identifier'], 'type': pm['typeCode']}, binance_id=pm['id']) for pm in pms]

    for coin in ("USDT", "BTC", "ETH", "BNB"):
        for cur in ("THB", "PHP", "GEL", "TRY"):
            for tt in TradeType:
                # rp = await sapi.get_ref_price([coin], cur, tt)
                r = await sapi.search_ads(coin, cur, tt.name)
                if r0 := r[0]["data"]["adv"]:
                    pd = {"fee": r0["commissionRate"], "price": r0["price"], "total": r[0]["total"]}
                    pms = [Pm.get(identifier=pm["identifier"]) for pm in r0["tradeMethods"]]
                    ad = {"price": r0["price"], "id": r0["total"]}
                    p, _ = await Pair.update_or_create(pd, ex_id=1, cur=cur, coin=coin, sell=tt.value)
                    a, _ = await Ad.update_or_create(ad, pair=p, cur=cur, coin=coin, sell=tt.value)
                    await a.pms.add(*pms)


if __name__ == "__main__":
    res = run(main())
    print(res)
