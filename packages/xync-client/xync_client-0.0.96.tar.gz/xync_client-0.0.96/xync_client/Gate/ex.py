from asyncio import run
import requests
from pyro_client.client.file import FileClient
from x_model import init_db
from xync_schema.models import Ex
from xync_schema import xtype

from xync_client.Abc.Ex import BaseExClient
from xync_client.loader import TOKEN, TORM
from xync_client.Abc.xtype import PmEx, MapOfIdsList
from xync_client.Gate.etype import ad


class ExClient(BaseExClient):
    logo_pre_url = "www.gate.io"

    _data: dict = {}

    # Данные для р2р из html Gate.io
    @property
    def data(self) -> (dict, dict, dict, dict):
        self._data = (
            self._data
            or requests.post(
                "https://www.gate.com/json_svr/query_push?u=p2p_common_trade_config",
                data={"type": "p2p_common_trade_config"},
            ).json()["datas"]
        )
        return self._data

    # 20: Список всех платежных методов на бирже
    async def pms(self, cur: str = None) -> dict[int | str, PmEx]:
        data = self.data
        return {
            p["pay_type"]: PmEx(exid=p["pay_type"], name=p["pay_name"], logo=p["image"])
            for p in (data["payment_settings"]).values()
        }

    # 21: Список поддерживаемых валют
    async def coins(self) -> dict[xtype.CoinEx]:
        data = self.data
        return {coin: xtype.CoinEx(exid=coin, ticker=coin) for coin in data["c2c_currencies"]}

    # 22: Списки поддерживаемых платежек по каждой валюте
    async def cur_pms_map(self) -> MapOfIdsList:
        data = self.data
        return data["fait_payment_settings"]

    async def pairs(self) -> MapOfIdsList:
        coins = (await self.coins()).keys()
        curs = (await self.curs()).keys()
        p = {cur: {c for c in coins} for cur in curs}
        return p, p

    # 23: Монеты на Gate
    async def curs(self) -> dict[xtype.CurEx]:
        data = self.data
        return {cur: xtype.CurEx(exid=cur, ticker=cur) for cur in data["c2c_fiats"]}

    # 24: ads
    async def ads(
        self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str | int] = None, amount: int = None
    ) -> list[ad.Ad]:
        data = {
            "type": "push_order_list",
            "symbol": f"{coin_exid}_{cur_exid}",
            "big_trade": "0",
            "fiat_amount": amount or "",
            "amount": "",
            "pay_type": pm_exids and ",".join(pm_exids) or "",
            "is_blue": "0",
            "is_crown": "0",
            "is_follow": "0",
            "have_traded": "0",
            "no_query_hide": "0",
            "per_page": "20",
            "push_type": "sell" if is_sell else "buy",
            "sort_type": "1",
            "page": "1",
        }
        ads = requests.post("https://www.gate.com/json_svr/query_push/", data=data)
        return [ad.Ad(id=_ad["uid"], price=_ad["rate"], **_ad) for _ad in ads.json()["push_order"]]


async def main():
    _ = await init_db(TORM, True)
    gt = await Ex.get(name="Gate")
    async with FileClient(TOKEN) as b:
        cl = ExClient(gt, b)
        await cl.set_pairs()
        pms = await cl.set_coins()
        pms = await cl.set_curs()
        pms = await cl.set_pms()
        _ads = await cl.ads("USDT", "RUB", True, ["payeer"], 1000)
        # curs = await cl.curs()
        # await cl.coins()
        print(pms)


if __name__ == "__main__":
    run(main())
