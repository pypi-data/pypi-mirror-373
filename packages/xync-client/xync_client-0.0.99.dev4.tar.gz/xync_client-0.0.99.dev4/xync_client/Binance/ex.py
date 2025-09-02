from asyncio import run

from pyro_client.client.file import FileClient
from x_model import init_db

from xync_client.Abc.Ex import BaseExClient
from xync_client.Binance.etype import pm, ad
from xync_client.Abc.xtype import PmEx, MapOfIdsList
from xync_client.loader import TOKEN, TORM

from xync_schema.models import Ex
from xync_schema import xtype
from xync_schema import models


class ExClient(BaseExClient):
    logo_pre_url = "bin.bnbstatic.com"

    async def _pms(self, cur) -> list[pm.PmE]:
        data = {
            "fiat": cur,
            "classifies": [
                "mass",
                "profession",
                "fiat_trade",
            ],
        }
        pms = await self._post("/bapi/c2c/v2/public/c2c/adv/filter-conditions", json=data)
        return [pm.PmE(**_pm) for _pm in pms["data"]["tradeMethods"]]

    async def curs(self) -> dict[int, xtype.CurEx]:
        curs = await self._post("/bapi/c2c/v1/friendly/c2c/trade-rule/fiat-list")
        return {
            c["currencyCode"]: xtype.CurEx(exid=c["currencyCode"], ticker=c["currencyCode"], scale=c["currencyScale"])
            for c in curs["data"]
        }

    async def coins(self) -> dict[int, xtype.CoinEx]:
        for cur in (await self.curs()).keys():
            coins = (await self._post("/bapi/c2c/v2/friendly/c2c/portal/config", {"fiat": cur}))["data"]["areas"][0][
                "tradeSides"
            ][0]["assets"]
            return {coin["asset"]: xtype.CoinEx(exid=coin["asset"], ticker=coin["asset"]) for coin in coins}

    async def pairs(self) -> MapOfIdsList:
        coins = (await self.coins()).keys()
        curs = (await self.curs()).keys()
        p = {cur: {c for c in coins} for cur in curs}
        return p, p

    async def pms(self, cur: models.Cur = None) -> dict[int | str, PmEx]:
        all_pms = {}
        for cur in (await self.curs()).values():
            pms = await self._pms(cur.ticker)
            for p in pms:
                all_pms[p.identifier] = PmEx(exid=p.identifier, name=p.tradeMethodName, logo=p.iconUrlColor)
        return all_pms

    # 22: Cur -> [Pm] rels
    async def cur_pms_map(self) -> MapOfIdsList:  # {cur.exid: [pm.exid], [pm.exid]}
        res = await self.curs()
        mp = {c: await self._get_pms_for_cur(c) for c in res.keys()}
        return mp

    # # 22: Cur -> [Pm] rels
    # async def cur_countries_map(self) -> dict[int, set[int]]:  # {cur.exid: [pm.exid]}
    #     res = await self._get_pms_and_country_for_cur()
    #     wrong_pms = {4, 34, 212, 239, 363, 498, 548, 20009, 20010}  # these ids not exist in pms
    #     return {c['currencyId']: set(c['supportPayments']) - wrong_pms for c in res['currency'] if c["supportPayments"]}

    async def ads(self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str] = None) -> list[ad.Ad]:
        pm_exids = pm_exids or []
        data = {
            "fiat": cur_exid,
            "page": 1,
            "rows": 10,
            "tradeType": "BUY" if is_sell else "SELL",
            "asset": coin_exid,
            "countries": [],
            "proMerchantAds": False,
            "shieldMerchantAds": False,
            "filterType": "all",
            "periods": [],
            "additionalKycVerifyFilter": 0,
            "publisherType": None,  # "merchant",
            "payTypes": pm_exids,
            "classifies": [
                "mass",
                "profession",
                "fiat_trade",
            ],
            "tradedWith": False,
            "followed": False,
        }
        ads = await self._post("/bapi/c2c/v2/friendly/c2c/adv/search", json=data)
        return [ad.Ad(id=_ad["adv"]["advNo"], price=_ad["adv"]["price"], **_ad) for _ad in ads["data"]]

    async def _get_pms_for_cur(self, cur: str) -> ([str], [str]):
        data = {"fiat": cur, "classifies": ["mass", "profession"]}
        res = await self._post("/bapi/c2c/v2/public/c2c/adv/filter-conditions", data)
        return [r["identifier"] for r in res["data"]["tradeMethods"]]
        # , [
        #     r["scode"] for r in res["data"]["countries"] if r["scode"] != "ALL"
        # ]  # countries,tradeMethods,periods


# class Private(Public): # todo: base class: Public or Client?
# class Private(Client):
#     # auth: dict =
#     headers: dict = {
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36",
#         "Content-Type": "application/json",
#         "clienttype": "web",
#     }
#
#     def seq_headers(self):
#         return {
#             "csrftoken": self.auth["tok"],
#             "cookie": f'p20t=web.{self.id}.{self.auth["cook"]}',
#         }


async def main():
    _ = await init_db(TORM)
    ex = await Ex.get(name="Binance")
    async with FileClient(TOKEN) as b:
        cl = ExClient(ex, b)
        await cl.set_pms()
        await cl.set_coins()
        await cl.set_pairs()
        # await cl.pairs()
        await cl.ads("ETH", "GEL", False)
        await cl.close()


if __name__ == "__main__":
    run(main())
