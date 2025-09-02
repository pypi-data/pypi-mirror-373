import logging
from asyncio import run

from pyro_client.client.file import FileClient
from x_model import init_db
from xync_schema.models import Ex
from xync_schema import xtype

from xync_client.Abc.Ex import BaseExClient
from xync_client.BingX.base import BaseBingXClient
from xync_client.loader import TOKEN, TORM
from xync_client.Abc.xtype import MapOfIdsList
from xync_client.BingX.etype import ad, pm
from xync_client.Abc.xtype import PmEx


class ExClient(BaseExClient, BaseBingXClient):
    headers: dict[str, str] = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "app_version": "9.0.5",
        "device_id": "ccfb6d50-b63b-11ef-b31f-ef1f76f67c4e",
        "lang": "en",
        "platformid": "30",
        "device_brand": "Linux_Chrome_131.0.0.0",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    async def _pms(self, cur) -> list[pm.PmE]:
        pms = await self._get("/api/c2c/v1/advert/payment/list", params={"fiat": cur})
        return [pm.PmE(**_pm) for _pm in pms["data"]["paymentMethodList"]]

    # 19: Список всех платежных методов на бирже
    async def pms(self, cur: str = None) -> dict[int | str, PmEx]:
        all_pms = {}
        for cur in (await self.curs()).values():
            pms = await self._pms(cur.ticker)
            for p in pms:
                all_pms[p.id] = PmEx(exid=p.id, name=p.name, logo=p.icon)
        return all_pms

    # 20: Список поддерживаемых валют на BingX
    async def curs(self) -> list[xtype.CurEx]:  # {cur.exid: cur.ticker}
        params = {
            "type": "1",
            "asset": "USDT",
            "coinType": "2",
        }
        curs = await self._get("/api/c2c/v1/common/supportCoins", params=params)
        return {cur["name"]: xtype.CurEx(exid=cur["name"], ticker=cur["name"]) for cur in curs["data"]["coins"]}

    # 21: cur_pms_map на BingX
    async def cur_pms_map(self) -> MapOfIdsList:
        return {cur.exid: [pm.id for pm in await self._pms(cur.ticker)] for cur in (await self.curs()).values()}

    # 22: Монеты на BingX
    async def coins(self) -> list[xtype.CoinEx]:
        return {"USDT": xtype.CoinEx(exid="USDT", ticker="USDT", scale=4)}

    # 23: Список пар валюта/монет
    async def pairs(self) -> MapOfIdsList:
        coins = (await self.coins()).keys()
        curs = (await self.curs()).keys()
        p = {cur: {c for c in coins} for cur in curs}
        return p, p

    # 24: ads
    async def ads(
        self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str | int] = None, amount: int = ""
    ) -> list[ad.Ad]:
        if len(pm_exids):
            if len(pm_exids) > 1:
                logging.error("BingX принимает только 1 платежный метод!")
            pm_exid = pm_exids[0]
        else:
            pm_exid = ""
        params = {
            "type": 1,
            "fiat": cur_exid,
            "asset": coin_exid,
            "amount": amount,
            "hidePaymentInfo": "",
            "payMethodId": pm_exid,
            "isUserMatchCondition": "true" if is_sell else "false",
        }

        ads = await self._get("/api/c2c/v1/advert/list", params=params)
        return [ad.Ad(id=_ad["orderNo"], **_ad) for _ad in ads["data"]["dataList"]]


async def main():
    _ = await init_db(TORM, True)
    bg = await Ex.get(name="BingX").prefetch_related("pm_reps")
    async with FileClient(TOKEN) as b:
        b: FileClient
        cl = ExClient(bg, b)
        _ads = await cl.ads(
            "USDT",
            "RUB",
            True,
        )
        await cl.set_pairs()
        await cl.set_coins()
        await cl.set_pms()
        # _curs = await cl.curs()
        # _coins = await cl.coins()
        # _pairs = await cl.pairs()
        # _pms = await cl.pms("EUR")
        # _pms_map = await cl.cur_pms_map()
        await cl.close()


if __name__ == "__main__":
    run(main())
