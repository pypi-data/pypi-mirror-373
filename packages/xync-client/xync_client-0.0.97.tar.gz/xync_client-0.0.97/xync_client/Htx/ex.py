from asyncio import run
from collections import defaultdict

from msgspec import convert
from pyro_client.client.file import FileClient
from x_model import init_db
from xync_schema import models, xtype
from xync_schema.models import Ex, Cur
from xync_schema.enums import PmType

from xync_client.Abc.Ex import BaseExClient
from xync_client.Abc.xtype import PmEx, MapOfIdsList
from xync_client.Htx.etype import pm, Country, ad
from xync_client.loader import TOKEN
from xync_client.loader import TORM


class ExClient(BaseExClient):
    cur_map = {
        # 1: "CNY",
        8: "KRW",
        25: "MMK",
    }

    _data: dict = {}

    def pm_type_map(self, typ: models.PmEx) -> str:
        pass

    async def pairs(self) -> tuple[MapOfIdsList, MapOfIdsList]:
        self.session.headers["client-type"] = "web"
        rcoins: dict[str, int] = {c.ticker: exid for exid, c in (await self.coins()).items()}
        rcurs: dict[str, int] = {c.ticker: exid for exid, c in (await self.curs()).items()}
        pairs = {"buy": defaultdict(list), "sell": defaultdict(list)}
        for side, pair in pairs.items():
            res = (await self._get("/-/x/otc/v1/trade/fast/config/list", {"side": side, "tradeMode": "c2c_simple"}))[
                "data"
            ]
            for coin in res:
                for cur in coin["quoteAsset"]:
                    if coen := rcoins.get(coin["cryptoAsset"]["name"]):
                        pair[rcurs[cur["name"]]] += [coen]
        return tuple(pairs.values())

    async def ads(
        self, coin_exid: int, cur_exid: int, is_sell: bool, pm_exids: list[str] = None, amount: int = None
    ) -> list[xtype.BaseAd]:
        params = {
            "coinId": coin_exid,
            "currency": cur_exid,
            "tradeType": "sell" if is_sell else "buy",
            "currPage": 1,
            "payMethod": ",".join(pm_exids) if pm_exids else 0,
            "acceptOrder": 0,
            "blockType": "general",
            "online": 1,
            "range": 0,
            "amount": amount or "",
            "onlyTradable": "false",
            "isFollowed": "false",
        }
        res = (await self._get("/-/x/otc/v1/data/trade-market", params))["data"]
        ads = [ad.Resp(**a) for a in res]
        return ads

    async def ad(self, ad_id: int) -> xtype.BaseAd:
        pass

    # 20: Get all pms
    async def pms(self, _cur: Cur = None) -> dict[int, PmEx]:
        dist = {
            0: PmType.card,
            1: PmType.bank,
            2: PmType.cash,
            3: PmType.emoney,
            4: PmType.emoney,
            5: PmType.IFSC,
        }

        pms: list[pm.Resp] = [convert(p, pm.Resp) for p in (await self.data)["payMethod"]]

        pmsd = {
            p.payMethodId: PmEx(
                exid=p.payMethodId,
                name=p.name,
                typ=dist.get(p.template),
                logo=p.bankImage or p.bankImageWeb,
            )
            for p in pms
        }

        return pmsd

    # 21: Get all: currency,pay,allCountry,coin
    async def curs(self) -> dict[int, xtype.CurEx]:
        self.session.headers["client-type"] = "web"
        curs: list[dict] = (await self.data)["currency"]
        cmap: dict[str, int] = {c["nameShort"]: c["currencyId"] for c in curs}
        res = (await self._get("/-/x/otc/v1/trade/fast/config/list", {"side": "sell", "tradeMode": "c2c_simple"}))[
            "data"
        ]
        cursd: dict[str, float] = {}
        for c in res:
            for q in c["quoteAsset"]:
                cursd[q["name"]] = max(cursd.get(q["name"], 0), float(q["minAmount"]))
        return {exid: xtype.CurEx(exid=exid, ticker=tkr, minimum=cursd.get(tkr)) for tkr, exid in cmap.items()}

    # 22: Список платежных методов по каждой валюте
    async def cur_pms_map(self) -> dict[int, set[int]]:
        res = await self.data
        wrong_pms = {4, 34, 498, 548, 20009, 20010}  # , 212, 239, 363  # these ids not exist in pms
        return {c["currencyId"]: set(c["supportPayments"]) - wrong_pms for c in res["currency"] if c["supportPayments"]}

    # 23: Список торгуемых монет
    async def coins(self) -> dict[int, xtype.CoinEx]:
        self.session.headers["client-type"] = "web"
        coins: list[dict] = (await self.data)["coin"]
        res = (await self._get("/-/x/otc/v1/trade/fast/config/list", {"side": "buy", "tradeMode": "c2c_simple"}))[
            "data"
        ]
        coinsl: list[str] = [c["cryptoAsset"]["name"] for c in res]
        return {
            c["coinId"]: xtype.CoinEx(exid=c["coinId"], ticker=c["coinCode"], scale=c["showPrecision"])
            for c in coins
            if c["coinCode"] in coinsl
        }

    # 99: Страны
    async def countries(self) -> list[Country]:
        cmap = {
            "Kazakstan": "Kazakhstan",
        }
        res = await self.data
        cts = [
            Country(
                id=c["countryId"],
                code=c["code"],
                name=cmap.get(ct := name[:-1] if (name := c["name"].split(",")[0]).endswith(".") else name, ct),
                short=c["appShort"],
                cur_id=c["currencyId"] if c["currencyId"] != 1 else 172,
            )
            for c in res["country"]
        ]
        return cts

    # Get all: currency,pay,allCountry,coin
    @property
    async def data(self) -> (dict, dict, dict, dict):
        self._data = (
            self._data
            or (await self._get("/-/x/otc/v1/data/config-list", {"type": "currency,pay,coin,allCountry"}))["data"]
        )
        return self._data


async def main():
    _ = await init_db(TORM, True)
    ex = await Ex.get(name="Htx")
    async with FileClient(TOKEN) as b:
        b: FileClient
        cl = ExClient(ex, b)
        await cl.set_curs()
        await cl.set_pms()
        await cl.set_coins()
        await cl.set_pairs()
        # _pms = await cl.pms()
        # _ads = await cl.ads(2, 11, True)
        await cl.close()


if __name__ == "__main__":
    run(main())
