from asyncio import run

from pyro_client.client.file import FileClient
from x_model import init_db
from xync_schema.models import Ex
from xync_schema import xtype

from xync_client.Abc.Ex import BaseExClient
from xync_client.loader import TORM, TOKEN
from xync_client.Abc.xtype import PmEx, MapOfIdsList
from xync_client.BitGet.etype import ad


class ExClient(BaseExClient):
    _data: dict = {}

    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://www.bitget.com/ru/p2p-trade",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    }

    async def _coin_cur_pms(self) -> dict:
        if not self._data:
            resp = await self.session.post(
                "/v1/p2p/pub/currency/queryAllCoinAndFiat",
                json={"languageType": 6},
                headers=self.headers,
            )
            res = await resp.json()
            self._data = res["data"]
        return self._data

    async def curs(self) -> dict[str, xtype.CurEx]:
        curs = (await self._coin_cur_pms())["fiatInfoRespList"]
        return {
            cur["fiatCode"]: xtype.CurEx(
                exid=cur["fiatCode"],
                ticker=cur["fiatCode"],
                scale=cur["fiatPrecision"],
                minimum=int(float(cur["orderMinLimit"])),
            )
            for cur in curs
        }

    async def coins(self) -> dict[str, xtype.CoinEx]:
        coins: list[dict] = (await self._coin_cur_pms())["coinInfoRespList"]
        return {
            coin["coinCode"]: xtype.CoinEx(
                exid=coin["coinCode"],
                ticker=coin["coinCode"],
                scale=coin["coinPrecision"],
                minimum=int(float(coin["orderMinLimit"])),
            )
            for coin in coins
        }

    async def pairs(self) -> MapOfIdsList:
        coins = (await self.coins()).keys()
        curs = (await self.curs()).keys()
        p = {cur: {c for c in coins} for cur in curs}
        return p, p

    async def pms(self, cur: str = None) -> dict[int | str, PmEx]:  # {pm.exid: pm}
        pp = {}
        pms: list[dict] = (await self._coin_cur_pms())["fiatInfoRespList"]
        for pm in pms:
            for p in pm["paymethodInfo"]:
                pp[p["paymethodId"]] = PmEx(exid=p["paymethodId"], name=p["paymethodName"], logo=p.get("iconUrl"))
        return pp

    async def ads(
        self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str | int] = None, amount: int = None
    ) -> list[ad.Ad]:
        request_data = {
            "side": 1 if is_sell else 2,
            "pageNo": 1,
            "pageSize": 10,
            "coinCode": coin_exid,
            "fiatCode": cur_exid,
            "paymethodIds": pm_exids or "",
            "languageType": 6,
        }
        resp = await self.session.post("/v1/p2p/pub/adv/queryAdvList", json=request_data, headers=self.headers)
        res = await resp.json()
        ads = res["data"]["dataList"]
        return [ad.Ad(**_ad) for _ad in ads]

    async def cur_pms_map(self) -> dict[str, list[int]]:
        cur_pms_map: list[dict] = (await self._coin_cur_pms())["fiatInfoRespList"]
        return {item["fiatCode"]: [pms["paymethodId"] for pms in item["paymethodInfo"]] for item in cur_pms_map}


async def main():
    _ = await init_db(TORM, True)
    bg = await Ex.get(name="BitGet")
    cl = ExClient(bg, FileClient(TOKEN))
    _ads = await cl.ads("USDT", "RUB", False, [])
    await cl.curs()
    await cl.coins()
    await cl.pms()
    await cl.cur_pms_map()
    await cl.set_pms()
    await cl.set_coins()
    await cl.close()


if __name__ == "__main__":
    run(main())
