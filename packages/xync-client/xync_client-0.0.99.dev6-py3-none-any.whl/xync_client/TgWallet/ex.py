from asyncio import run, sleep

from pyro_client.client.file import FileClient
from x_model import init_db
from xync_schema import xtype
from xync_schema import models
from xync_schema.xtype import AdBuyIn

from xync_client.Abc.xtype import PmEx
from xync_client.TgWallet.pyd import (
    PmEpydRoot,
    OneAdTakerMakerSale,
    OneAdTakerBuy,
    AdTakerSaleBuy,
    _TakerOne,
    _PmsTrait,
    _BaseAd,
)
from xync_client.loader import TOKEN, TORM
from xync_client.Abc.Ex import BaseExClient
from xync_client.Abc.xtype import MapOfIdsList
from xync_client.TgWallet.auth import AuthClient


class ExClient(BaseExClient, AuthClient):
    coin_scales = {
        "USDT": 6,
        "TON": 9,
        "BTC": 8,
        "ETH": 8,
        "NOT": 9,
    }

    def __init__(self, ex: models.Ex, bot: FileClient, actor: models.Actor = None):
        if actor:
            self.actor = actor
        super().__init__(ex, bot)  # BaseExClient

    def pm_type_map(self, pm: models.Pm) -> str:
        # todo: no pm.name
        return "V2" if pm.norm.startswith("SBP") else "V1"

    # 00: todo: min-max for cur and coin ad amount, order, fee ..
    async def _settings(self) -> dict:
        settings = await self._post("/p2p/public-api/v2/offer/settings/get")
        return settings["data"]

    # 19: Список поддерживаемых валют тейкера
    async def curs(self) -> dict[str, xtype.CurEx]:
        coins_curs = await self._post("/p2p/public-api/v2/currency/all-supported")
        stg = await self._settings()
        roundings: dict[str, int] = stg["offerSettings"]["roundingScaleByFiatCurrency"]
        minimums: dict[str, str] = stg["offerSettings"]["minOrderAmountByCurrencyCode"]
        return {
            c["code"]: xtype.CurEx(
                exid=c["code"], ticker=c["code"], scale=roundings.get(c["code"]), minimum=minimums[c["code"]]
            )
            for c in coins_curs["data"]["fiat"]
        }

    async def _pms(self, cur: str) -> dict[str, PmEpydRoot]:
        pms = await self._post("/p2p/public-api/v3/payment-details/get-methods/by-currency-code", {"currencyCode": cur})
        return {pm["code"]: PmEpydRoot(**pm) for pm in pms["data"]}

    # 20: Список платежных методов. todo: refact to pmexs?
    async def pms(self, cur: str = None) -> dict[str, PmEx]:
        pms: dict[str:PmEpydRoot] = {}
        if cur:
            pms = await self._pms(cur)
        else:
            for cur in (await self.curs()).values():
                pms |= await self._pms(cur.exid)
        return {
            k: PmEx(
                exid=pm.code,
                name=pm.nameEng,
                banks=[xtype.PmExBank(exid=b.code, name=b.name) for b in pm.banks or []],
            )
            for k, pm in pms.items()
        }

    # 21: Список платежных методов по каждой валюте
    async def cur_pms_map(self) -> MapOfIdsList:
        return {cur.exid: list(await self._pms(cur.exid)) for cur in (await self.curs()).values()}

    # 22: Список торгуемых монет (с ограничениям по валютам, если есть)
    async def coins(self) -> dict[str, xtype.CoinEx]:
        coins_curs = await self._post("/p2p/public-api/v2/currency/all-supported")
        stg = await self._settings()
        lims = list(stg["offerSettings"]["offerVolumeLimitsPerMarket"].values())
        coins = {k: max(float(v[k]["minInclusive"]) for v in lims) for k, v in lims[0].items()}
        return {
            c["code"]: xtype.CoinEx(exid=c["code"], ticker=c["code"], minimum=coins[c["code"]])
            for c in coins_curs["data"]["crypto"]
        }

    # 23: Список пар валюта/монет
    async def pairs(self) -> tuple[MapOfIdsList, MapOfIdsList]:
        coins = await self.coins()
        curs = await self.curs()
        pairs = {cur.exid: set(c.exid for c in coins.values()) for cur in curs.values()}
        return pairs, pairs

    # 42: Чужая объява по id
    async def ad(self, ad_id: int) -> _TakerOne:
        ad = await self._post("/p2p/public-api/v2/offer/get", {"offerId": ad_id})
        if not ad or not (ad := ad.get("data")):
            return ad
        model = OneAdTakerMakerSale if ad["type"] == "SALE" else OneAdTakerBuy
        return model(**ad)

    # 24: Список объяв по (buy/sell, cur, coin, pm)
    async def ads(
        self, coin_exid: str, cur_exid: str, is_sell: bool, pm_exids: list[str | int] = None, amount: int = None
    ) -> list[AdTakerSaleBuy]:
        params = {
            "baseCurrencyCode": coin_exid,
            "quoteCurrencyCode": cur_exid,
            "offerType": "SALE" if is_sell else "PURCHASE",
            "offset": 0,
            "limit": 100,
            # "merchantVerified": "TRUSTED"
        }
        ads = await self._post("/p2p/public-api/v2/offer/depth-of-market/", params, "data")
        return [AdTakerSaleBuy(**ad) for ad in ads]

    async def ad_common_epyd2pydin(self, ad: _BaseAd) -> xtype.BaseAdIn:
        coin = await models.Coin.get_or_create_by_name(ad.price.baseCurrencyCode)
        cur = await models.Cur.get_or_create_by_name(ad.price.quoteCurrencyCode)
        pair, _ = await models.Pair.get_or_create(coin=coin, cur=cur)
        pairex, _ = await models.PairEx.get_or_create(pair=pair, ex=self.ex)
        dr, _ = await models.Direction.get_or_create(pairex=pairex, sell=ad.is_sell)
        return xtype.BaseAdIn(
            id=ad.id,
            price=ad.price.value,
            min_fiat=ad.orderAmountLimits.min,
            amount=float(ad.availableVolume.amount) * float(ad.price.estimated),
            max_fiat=ad.orderAmountLimits.max,
            direction_id=dr.id,
            detail=getattr(ad, "comment", None),
        )

    async def ad_taker_epyd2pydin(self, ad: _TakerOne) -> xtype.AdBuyIn:
        adx: xtype.BaseAdIn = await self.ad_common_epyd2pydin(ad)
        act_unq = dict(ex=self.ex, exid=ad.user.userId)
        if not (actor := await models.Actor.get_or_none(**act_unq)):
            actor = await models.Actor.create(**act_unq, name=ad.user.nickname, person=await models.Person.create())
        adx.maker = actor
        pms = ad.paymentMethods if isinstance(ad, _PmsTrait) else [pd.paymentMethod for pd in ad.paymentDetails]
        return xtype.AdBuyIn(
            **adx.model_dump(by_alias=True),
            pms_=await models.Pm.filter(pmexs__ex=self.ex, pmexs__exid__in=[p.code for p in pms]),
        )


async def _test():
    await init_db(TORM)
    tgex = await models.Ex.get(name="TgWallet")
    async with FileClient(TOKEN) as b:
        cl: ExClient = tgex.client(b)

        await cl.set_coins()
        await cl.set_curs()
        await cl.set_pairs()
        await cl.set_pms()
        # # # SALE # # #
        # get ads list
        ads: list[AdTakerSaleBuy] = await cl.ads("TON", "RUB", True)
        # prepare ad list items for saving
        ads_pydin: list[xtype.BaseAdIn] = [await cl.ad_taker_epyd2pydin(adp) for adp in ads]
        # list items save
        _ads_db = [await cl.ad_pydin2db(adi) for adi in ads_pydin]

        # get ad fulls
        ads_pyd: list[_TakerOne] = [await cl.ad(ad.exid) for ad in ads]
        # prepare ad fulls for saving
        ads_pydin: list[AdBuyIn] = [await cl.ad_taker_epyd2pydin(adp) for adp in ads_pyd]
        # full ones save
        _ads_db = [await sleep(0.1, await cl.ad_pydin2db(adi)) for adi in ads_pydin]

        # # # BUY # # #
        # get ads list
        ads: list[AdTakerSaleBuy] = await cl.ads("TON", "RUB", False)
        # prepare ad list items for saving
        ads_pydin: list[xtype.BaseAdIn] = [await cl.ad_taker_epyd2pydin(adp) for adp in ads]
        # list items save
        _ads_db = [await cl.ad_pydin2db(adi) for adi in ads_pydin]

        # get ad fulls
        ads_pyd = [await cl.ad(ad.exid) for ad in ads]
        # prepare ad fulls for saving
        ads_pydin: list[AdBuyIn] = [await cl.ad_taker_epyd2pydin(adp) for adp in ads_pyd]
        # full ones save
        _ads_db = [await cl.ad_pydin2db(adi) for adi in ads_pydin]

        await cl.close()


if __name__ == "__main__":
    run(_test())
