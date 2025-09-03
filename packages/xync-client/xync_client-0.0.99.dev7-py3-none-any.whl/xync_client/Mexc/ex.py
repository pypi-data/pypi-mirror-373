from asyncio import run

from pyro_client.client.file import FileClient
from x_model import init_db
import requests
from xync_client.loader import TORM, TOKEN

from xync_client.Abc.Ex import BaseExClient
from xync_client.Abc.xtype import PmEx, MapOfIdsList
from xync_client.Mexc.etype import pm, ad

from xync_schema import xtype
from xync_schema import models
from xync_schema.models import Ex


class ExClient(BaseExClient):
    logo_headers = {
        "accept-language": "ru,en;q=0.9",
        "priority": "u=0, i",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-site": "none",  # work from CURL, not work from aiohttp with no this header
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }
    logo_pre_url = "www.mexc.com/api/file/download"

    async def _pms(self, cur) -> list[pm.PmE]:
        pms = requests.get("https://p2p.mexc.com/api/payment/method", params={"currency": cur}).json()
        return [pm.PmE(**_pm) for _pm in pms["data"]]

    # 19: Список поддерживаемых валют тейкера
    async def curs(self) -> dict[str, xtype.CurEx]:  # {cur.ticker: cur}
        _curs = requests.get("https://p2p.mexc.com/api/common/currency").json()
        return {
            cur["currency"]: xtype.CurEx(exid=cur["currency"], ticker=cur["currency"], scale=cur["scale"])
            for cur in _curs["data"]
        }

    # 20: Список платежных методов
    async def pms(self, cur: models.Cur = None) -> dict[int | str, PmEx]:  # {pm.exid: pm}
        all_pms = {}
        for cur in (await self.curs()).values():
            pms = await self._pms(cur.ticker)
            for p in pms:
                all_pms[p.id] = PmEx(exid=p.id, name=p.name, logo=p.icon)
        return all_pms

    # 21: Список платежных методов по каждой валюте
    async def cur_pms_map(self) -> MapOfIdsList:  # {cur.exid: [pm.exid]}
        return {cur.exid: [pm.id for pm in await self._pms(cur.ticker)] for cur in (await self.curs()).values()}

    # 22: Список торгуемых монет (с ограничениям по валютам, если есть)
    async def coins(self) -> dict[str, xtype.CoinEx]:  # {coin.ticker: coin}
        coins = requests.get("https://p2p.mexc.com/api/common/coins").json()
        return {
            coin["coinId"]: xtype.CoinEx(exid=coin["coinId"], ticker=coin["coinName"], scale=coin["quantityScale"])
            for coin in coins["data"]
        }

    # 23: Список пар валюта/монет
    async def pairs(self) -> tuple[MapOfIdsList, MapOfIdsList]:
        coins = (await self.coins()).keys()
        curs = (await self.curs()).keys()
        p = {cur: {c for c in coins} for cur in curs}
        return p, p

    # 24: Список объяв по (buy/sell, cur, coin, pm)
    async def ads(
        self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str | int] = None, amount: int = None
    ) -> list[ad.Ad]:  # {ad.id: ad}
        params = {
            "allowTrade": "false",
            "amount": amount or "",
            "blockTrade": "false",
            "coinId": coin_exid,
            "countryCode": "",
            "currency": cur_exid,
            "follow": "false",
            "haveTrade": "false",
            "page": "1",
            "payMethod": pm_exids or "",
            "tradeType": "SELL" if is_sell else "BUY",
        }

        ads = requests.get("https://p2p.mexc.com/api/market", params=params).json()
        return [ad.Ad(**_ad) for _ad in ads["data"]]


async def main():
    _ = await init_db(TORM)
    async with FileClient(TOKEN) as b:
        ex = await Ex.get(name="Mexc")
        cl = ex.client(b)
        # await ex.curexs.filter(cur__ticker="EUR")
        # await cl.set_pms()
        # await cl.set_coinexs()
        _ads = await cl.ads("USDT", "EUR", True)
        _cr = await cl.curs()
        _cn = await cl.coins()
        await cl.set_pairs()
        _pms = await cl.pms()
        await cl.close()


if __name__ == "__main__":
    run(main())
