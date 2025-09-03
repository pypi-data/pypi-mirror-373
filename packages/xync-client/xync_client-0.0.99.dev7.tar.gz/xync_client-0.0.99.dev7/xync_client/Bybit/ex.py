import json
from asyncio import run

from pyro_client.client.file import FileClient
from x_model import init_db
from xync_schema import models, xtype
from xync_schema.models import Ex, Agent

from xync_client.Abc.Ex import BaseExClient
from xync_client.loader import TOKEN
from xync_client.Bybit.etype import ad
from xync_client.Abc.xtype import PmEx, MapOfIdsList
from xync_client.loader import TORM


class ExClient(BaseExClient):  # Bybit client
    headers = {"cookie": ";"}  # rewrite token for public methods
    agent: Agent = None

    async def _get_auth_cks(self) -> dict[str, str]:
        if not self.agent:
            self.agent = await Agent.get(actor__ex=self.ex).prefetch_related("actor")
        return self.agent.auth["cookies"]

    async def _get_config(self):
        resp = await self._get("/fiat/p2p/config/initial")
        return resp["result"]  # todo: tokens, pairs, ...

    # 19: Список поддерживаемых валют тейкера
    async def curs(self) -> dict[int, xtype.CurEx]:
        config = await self._get_config()
        return {
            c["currencyId"]: xtype.CurEx(exid=c["currencyId"], ticker=c["currencyId"], scale=c["scale"])
            for c in config["currencies"]
        }

    # 20: Список платежных методов
    async def pms(self, cur: models.Cur = None) -> dict[int | str, PmEx]:
        self.session.cookie_jar.update_cookies(await self._get_auth_cks())
        pms = await self._post("/fiat/otc/configuration/queryAllPaymentList/")
        self.session.cookie_jar.clear()

        pms = pms["result"]["paymentConfigVo"]
        return {pm["paymentType"]: PmEx(exid=pm["paymentType"], name=pm["paymentName"]) for pm in pms}

    # 21: Список платежных методов по каждой валюте
    async def cur_pms_map(self) -> MapOfIdsList:
        self.session.cookie_jar.update_cookies(await self._get_auth_cks())
        pms = await self._post("/fiat/otc/configuration/queryAllPaymentList/")
        return json.loads(pms["result"]["currencyPaymentIdMap"])

    # 22: Список торгуемых монет (с ограничениям по валютам, если есть)
    async def coins(self) -> dict[str, xtype.CoinEx]:
        config = await self._get_config()
        coinexs = {}
        for c in config["symbols"]:
            coinexs[c["tokenId"]] = xtype.CoinEx(
                exid=c["tokenId"], ticker=c["tokenId"], minimum=c["tokenMinQuote"], scale=c["token"]["scale"]
            )
        return coinexs

    # 23: Список пар валюта/монет
    async def pairs(self) -> tuple[MapOfIdsList, MapOfIdsList]:
        config = await self._get_config()
        cc: dict[str, set[str]] = {}
        for c in config["symbols"]:
            cc[c["currencyId"]] = cc.get(c["currencyId"], set()) | {c["tokenId"]}
        return cc, cc

    # 24: Список объяв по (buy/sell, cur, coin, pm)
    async def ads(
        self,
        coin_exid: str,
        cur_exid: str,
        is_sell: bool,
        pm_exids: list[str | int] = None,
        amount: int = None,
        lim: int = 50,
        vm_filter: bool = False,
    ) -> list[ad.Ad]:
        data = {
            "userId": "",
            "tokenId": coin_exid,
            "currencyId": cur_exid,
            "payment": pm_exids or [],
            "side": "0" if is_sell else "1",
            "size": str(lim) if lim else "20",
            "page": "1",
            "amount": str(amount) if amount else "",
            "vaMaker": vm_filter,
            "bulkMaker": False,
            "canTrade": False,
            "verificationFilter": 0,
            "sortType": "OVERALL_RANKING",
            "paymentPeriod": [],
            "itemRegion": 1,
        }
        # {
        #     "userId": "",
        #     "tokenId": coin_exid,
        #     "currencyId": cur_exid,
        #     "payment": pm_exids or [],
        #     "side": "0" if is_sell else "1",
        #     "size": lim and str(lim) or "200",
        #     "page": "1",
        #     "amount": str(amount) if amount else "",
        #     "authMaker": False,
        #     "canTrade": False,
        # }
        ads = await self._post("/fiat/otc/item/online/", data)
        return [ad.Ad(**_ad) for _ad in ads["result"]["items"]]


async def main():
    _ = await init_db(TORM, True)
    ex = await Ex.get(name="Bybit")
    bot: FileClient = FileClient(TOKEN)
    # await bot.start()
    cl = ExClient(ex, bot)
    await cl.set_pms()
    await cl.set_coins()
    await cl.set_pairs()
    _ads = await cl.ads("USDT", "GEL", False)
    # await bot.stop()
    await cl.close()


if __name__ == "__main__":
    run(main())
