import logging
from asyncio import run
from enum import StrEnum
from http.client import HTTPException

from x_model import init_db

from xync_client.Abc.xtype import BaseOrderReq
from xync_client.TgWallet.ex import ExClient
from xync_schema import models

from xync_client.TgWallet.pyd import (
    CredEpyd,
    Attrs,
    AttrsV2,
    OneAdTakerMakerSale,
    OneAdMakerBuy,
    AdMakerBuy,
    AdMakerSale,
    AdMakerNewSale,
    _AdNew,
    _PmsTrait,
    OneAdTakerBuy,
    OrderEpyd,
    AdMakerNewBuy,
    AvailableAmountVolume,
    CredEpydNew,
    CredEpydUpd,
    Banks,
    OrderAmountReq,
    OrderVolumeReq,
    OrderReqTrait,
)
from xync_client.loader import PG_DSN
from xync_schema.enums import AdStatus, UserStatus, OrderStatus

from xync_client.Abc.Base import ListOfDicts
from xync_client.TgWallet.auth import AuthClient
from xync_schema.xtype import BaseAdIn, AdBuyIn, AdSaleIn, OrderIn

from xync_client.Abc.Agent import BaseAgentClient


class Exceptions(StrEnum):
    ORDER_KYC = "FIAT_COUNTRY_NOT_SUPPORTED_BY_USER_KYC_COUNTRY"
    PM_KYC = "OFFER_FIAT_COUNTRY_NOT_SUPPORTED_BY_USER_KYC_COUNTRY"
    ROUND = "ROUNDING_IS_NOT_SUPPORTED"
    CUR = "CURRENCY_IS_NOT_SUPPORTED_BY_PAYMENT_METHOD"
    MAX_ADS = "ACTIVE_OFFER_COUNT_LIMIT_REACHED"
    INACTIVE_AD = "OFFER_ILLEGAL_STATE"
    FF = "CANNOT_DELETE_WHEN_USED_IN_OFFER"
    RESTRICTED = "RESTRICTED"


# class Status(IntEnum):
#     ALL_ACTIVE = OrderStatus.active


class AgentClient(BaseAgentClient, AuthClient):
    ex_client: ExClient

    # 0: Получение ордеров в статусе status, по монете coin, в валюте coin, в направлении is_sell
    async def orders(
        self,
        status: OrderStatus = OrderStatus.created,
        # coin: models.Coin = None,
        # cur: models.Cur = None,
        # is_sell: bool = None,
    ) -> ListOfDicts:
        order = await self._post(
            "/p2p/public-api/v2/offer/order/history/get-by-user-id",
            # {"offset": 0, "limit": 100, "filter": {"status": "ALL_ACTIVE"}},  # "limit": 20
            {"offset": 0, "limit": 100, "filter": {"status": status}},
        )
        return order["data"]

    # 0: Получение ордера по ид
    async def order(self, oid) -> ListOfDicts:
        orders = await self._post("/p2p/public-api/v2/offer/order/get", {"orderId": oid})
        return orders["data"]

    async def order_ad2epydin(self, ad: models.Ad, amount: float, cred_id: int = None) -> OrderReqTrait:
        if not cred_id:  # i am taker
            iam_maker = self.actor.id == ad.maker_id
            iam_seller = ad.direction.sell == iam_maker
            cred_filter = (
                {"person_id": self.actor.person_id}
                if iam_seller
                else {  # its a buy ad, i am taker
                    "actor": ad.maker
                }
            )
            await models.Cred.filter(
                **cred_filter,
                pmcur__pms__in=ad.pms,
                # todo: ordering and filtering by fiat.amount-target
            ).first() if iam_seller else 0
        await ad.fetch_related("direction__pairex__pair__cur")
        return OrderAmountReq(
            offerId=ad.exid,
            amount=AvailableAmountVolume(currencyCode=ad.direction.pairex.pair.cur.ticker, amount=str(int(amount))),
            type="SALE" if ad.direction.sell else "PURCHASE",
            paymentDetailsId=cred_id,
        )

    # 1: [T] Запрос на старт сделки
    async def order_request(self, base_req: BaseOrderReq) -> OrderEpyd | dict:
        credex = await models.CredEx.get(cred_id=base_req.cred_id, ex=self.ex)
        common = OrderReqTrait(
            offerId=base_req.ad_id, type="SALE" if base_req.is_sell else "BUY", paymentDetailsId=credex.exid
        )
        ad = await models.Ad.get(exid=base_req.ad_id).prefetch_related(
            "direction__pairex__pair__cur" if base_req.fiat_amount else "direction__pairex__pair__coin"
        )
        amount = AvailableAmountVolume(
            currencyCode=ad.direction.pairex.pair.cur.ticker
            if base_req.fiat_amount
            else ad.direction.pairex.pair.coin.ticker,
            amount=str(base_req.fiat_amount if base_req.fiat_amount else base_req.asset_amount),
        )
        req = (
            OrderAmountReq(**common.model_dump(), amount=amount)
            if base_req.fiat_amount
            else OrderVolumeReq(**common.model_dump(), volume=amount)
        )
        request = await self._post(
            f"/p2p/public-api/v2/offer/order/create-by-{'amount' if base_req.fiat_amount else 'volume'}",
            req.model_dump(exclude_none=True),
        )
        if r := request.get("data"):
            res = await self._post("/p2p/public-api/v2/offer/order/confirm", {"orderId": r["id"], "type": req.type})
            if res.get("status") == "SUCCESS":
                return OrderEpyd(**r)
        logging.error(request)
        return request

    async def order_epyd2pydin(self, order: OrderEpyd) -> OrderIn:
        ad = await models.Ad.get(exid=order.offerId, direction__pairex__ex=self.ex)
        cred = await models.Cred.get(exid=order.paymentDetails.id, actor__ex=self.ex)
        iam_maker = self.actor == ad.maker
        taker = (
            (
                await models.Actor.get(
                    exid=(order.seller if order.is_sell == iam_maker else order.buyer).userId, ex=self.ex
                )
            )
            if iam_maker
            else self.actor
        )
        return OrderIn(
            exid=order.id,
            amount=order.amount.amount,
            maker_topic=None,
            taker_topic=None,
            status=OrderStatus.created,
            created_at=order.createDateTime,
            payed_at=None,
            confirmed_at=None,
            appealed_at=None,
            ad=ad,
            cred=cred,
            taker=taker,
        )

    @staticmethod
    async def order_pydin2db(order: OrderIn) -> models.Order:
        df, unq = order.args()
        order_db, _ = await models.Order.update_or_create(df, **unq)
        return order_db

    # # # CREDS # # #
    @staticmethod
    def fiat_args2ex_pyd(exid: int | str, cur: str, detail: str, name: str, typ: str, extra=None) -> CredEpyd:
        cred = CredEpyd(
            paymentMethodCode=exid,
            currencyCode=cur,
            name=name,
            attributes=Attrs(
                version=typ,
                values=[Attrs.KeyVal(name={"V1": "PAYMENT_DETAILS_NUMBER", "V2": "PHONE"}[typ], value=detail)],
            ),
        )
        if typ == "V2":
            assert issubclass(extra, list) and extra, "extra should not be empty on V2 type"
            cred.attributes.values.append(
                AttrsV2.KeyVal(
                    name="BANKS",
                    value=extra,  # ["bank1", "bank2"]
                )
            )
        return cred

    @staticmethod
    def fiat_args2upsert(exid: int | str, cur: str, detail: str, name: str, fid: int = None) -> dict:
        return {
            **({"id": fid} if fid else {}),
            "paymentMethodCode": exid,
            "currencyCode": cur,
            "name": name,
            "attributes": {"version": "V1", "values": [{"name": "PAYMENT_DETAILS_NUMBER", "value": detail}]},
        }

    # 25: Список реквизитов моих платежных методов
    async def creds(self) -> list[CredEpyd]:
        resp = await self._post("/p2p/public-api/v3/payment-details/get/by-user-id")
        return [CredEpyd(**cred) for cred in resp["data"]]

    async def cred_epyd2db(self, cred: CredEpyd) -> models.CredEx:
        if not (pmex := await models.PmEx.get_or_none(exid=cred.paymentMethod.code, ex=self.ex_client.ex)):
            raise HTTPException(f"No PmEx {cred.paymentMethod.code} on ex#{self.ex_client.ex.name}", 404)
        if not (pmcur := await models.PmCur.get_or_none(cur__ticker=cred.currency, pm_id=pmex.pm_id)):
            raise HTTPException(f"No PmCur with cur#{cred.currency} and pm#{cred.paymentMethod.code}", 404)
        if not (person := await models.Person.get_or_none(actors__exid=cred.userId)):
            raise HTTPException(f"No PmCur with cur#{cred.currency} and pm#{cred.paymentMethod.code}", 404)
        dct = {"pmcur_id": pmcur.id, "name": cred.name, "person_id": person.id}
        banks: list[str] | None = None
        for val in cred.attributes.values:
            if val.name == "BANKS":
                val: Banks
                banks = [b.code for b in val.value]
            else:
                dct["detail"] = val.value
        cred_in = models.Cred.validate(dct, False)
        cred_db, _ = await models.Cred.update_or_create(**cred_in.df_unq())
        credex_in = models.CredEx.validate({"exid": cred.id, "cred_id": cred_db.id, "ex_id": self.ex.id})
        if banks:  # only for SBP
            await cred_db.banks.add(*[await models.PmExBank.get(exid=b) for b in banks])
        credex_db, _ = await models.CredEx.update_or_create(**credex_in.df_unq())
        return credex_db

    # 25: Список реквизитов моих платежных методов
    async def set_creds(self) -> list[models.CredEx]:
        creds_epyd: list[CredEpyd] = await self.creds()
        credexs: list[models.CredEx] = [await self.cred_epyd2db(f) for f in creds_epyd]
        return credexs

    async def challenge(self, name: str, payload: dict):
        req = {
            "deviceSerial": self.actor.agent.auth["ds"],
            "language": "en",
            "operation": {"name": name, "payload": payload},
        }
        if pas := self.actor.agent.auth.get("pass"):
            req["passcode"] = pas
        return await self._post("/v2api/challenges", req)

    # 26: Создание реквизита моего платежного метода
    async def cred_new(self, cred: models.Cred) -> models.CredEx:
        pmcur: models.PmCur = await cred.pmcur
        exid = await models.PmEx.get(pm_id=pmcur.pm_id, ex=self.ex_client.ex).values_list("exid", flat=True)
        cur = await models.Cur[pmcur.cur_id]
        vals = (
            [
                {"name": "PHONE", "value": cred.detail.replace(" ", "")},
                {"name": "BANKS", "value": [b.exid for b in banks]},
            ]
            if (banks := await cred.banks)
            else [{"name": "PAYMENT_DETAILS_NUMBER", "value": cred.detail}]
        )
        cred_new = CredEpydNew(
            paymentMethodCode=exid,
            currencyCode=cur.ticker,
            name=cred.name,
            attributes={"version": "V2" if banks else "V1", "values": vals},
        ).model_dump()
        if self.actor.agent.auth.get("ds"):
            challenge = await self.challenge("p2p/create-payment-details", cred_new)
            hdrs = {
                "x-wallet-operation-token": challenge["operationToken"],
                "x-wallet-device-serial": self.actor.agent.auth["ds"],
            }
        else:
            hdrs = {}
        add_cred = await self._post("/p2p/public-api/v3/payment-details/create", cred_new, headers=hdrs)
        cred_epyd = CredEpyd(**add_cred["data"])
        return await self.cred_epyd2db(cred_epyd)

    # 27: Редактирование реквизита моего платежного метода
    async def cred_upd(self, cred: models.Cred, exid: int) -> models.CredEx:
        pmcur: models.PmCur = await cred.pmcur
        pmex = await models.PmEx.get(pm_id=pmcur.pm_id, ex=self.ex_client.ex)
        cur = await models.Cur[pmcur.cur_id]
        vals = (
            [{"name": "PHONE", "value": cred.detail}, {"name": "BANKS", "value": [b.exid for b in banks]}]
            if (banks := await cred.banks)
            else [{"name": "PAYMENT_DETAILS_NUMBER", "value": cred.detail}]
        )
        cred_upd = CredEpydUpd(
            id=exid,
            paymentMethodCode=pmex.exid,
            currencyCode=cur.ticker,
            name=cred.name,
            attributes={"version": "V2" if banks else "V1", "values": vals},
        ).model_dump()
        challenge = await self.challenge("p2p/edit-payment-details", cred_upd)
        hdrs = {
            "x-wallet-operation-token": challenge["operationToken"],
            "x-wallet-device-serial": self.actor.agent.auth["ds"],
        }
        edit_cred = await self._post("/p2p/public-api/v3/payment-details/edit", cred_upd, headers=hdrs)
        cred_epyd = CredEpyd(**edit_cred["data"])
        return await self.cred_epyd2db(cred_epyd)

    # 28: Удаление реквизита моего платежного метода
    async def cred_del(self, cred_id: int) -> int:  # exid
        res: dict = await self._post("/p2p/public-api/v3/payment-details/delete", {"id": cred_id})
        if res.get("status") == "SUCCESS":
            await (await models.CredEx.get(exid=cred_id)).delete()
            return res["data"]["id"]
        else:
            logging.error(res)

    async def ad_epyd2pydin(self, ad_: OneAdTakerMakerSale | OneAdMakerBuy | OneAdTakerBuy) -> AdBuyIn | AdSaleIn:
        ad_in: BaseAdIn = await self.ex_client.ad_common_epyd2pydin(ad_)
        ad_in.maker_id = self.actor.id
        if isinstance(ad_, _PmsTrait):
            return AdBuyIn(
                **ad_in.model_dump(),
                pmexs_=await models.PmEx.filter(ex=self.ex_client.ex, exid__in=[p.code for p in ad_.paymentMethods]),
            )
        credsexs: list[models.CredEx] = [await self.cred_epyd2db(c) for c in ad_.paymentDetails]
        return AdSaleIn(**ad_in.model_dump(), credexs_=credsexs)

    # 29: Список моих объявлений
    async def my_ads(self, status: AdStatus = None) -> list[AdMakerBuy | AdMakerSale]:
        def model(ad: dict) -> (AdMakerBuy | AdMakerSale).__class__:
            return AdMakerSale if ad["type"] == "SALE" else AdMakerBuy

        mapping = {AdStatus.defActive: "INACTIVE", AdStatus.active: "ACTIVE"}
        ads = await self._post(
            "/p2p/public-api/v2/offer/user-own/list",
            {"offset": 0, "limit": 20},  # , "offerType": "SALE"|"PURCHASE"
        )
        return [model(ad)(**ad) for ad in ads["data"] if not status or (status and ad["status"] == mapping[status])]

    # 43: Моя объява по id
    async def my_ad(self, ad_id: int) -> OneAdMakerBuy | OneAdTakerMakerSale:
        ad = await self._post("/p2p/public-api/v2/offer/get-user-own", {"offerId": ad_id})
        ad: dict = ad["data"]
        assert ad["user"]["userId"] == self.actor.exid, "Not your ad"
        model = OneAdTakerMakerSale if ad["type"] == "SALE" else OneAdMakerBuy
        return model(**ad)

    async def ad_f2ein(
        self, coin: models.Coin, cur: models.Cur, is_sell: bool, vol: int = None, cur_min: int = None
    ) -> AdMakerNewSale | AdMakerNewBuy:
        coinex = await models.CoinEx.get(coin=coin, ex=self.ex)
        curex = await models.CurEx.get(ex=self.ex, cur=cur)
        credexs = (
            await models.CredEx.filter(cred__person_id=self.actor.person_id, cred__pmcur__cur=cur)
            .limit(5)
            .prefetch_related("cred")
        )
        # todo: ordering and filtering by fiat.amount-target
        ad_ein = _AdNew(
            type="SALE" if is_sell else "PURCHASE",
            initVolume=AvailableAmountVolume(currencyCode=coinex.exid, amount=str(vol or coinex.minimum)),
            orderRoundingRequired=curex.scale is not None,
            price={
                "type": "FLOATING",
                "baseCurrencyCode": coinex.exid,
                "quoteCurrencyCode": curex.exid,
                "value": "120" if is_sell else "80",
            },
            orderAmountLimits={"min": str(cur_min or curex.minimum)},
            paymentConfirmTimeout="PT15M",
            comment="tst",
        )
        if ad_ein.type == "SALE":
            ad_ein = AdMakerNewSale(**ad_ein.model_dump(exclude_none=True), paymentDetailsIds=[c.exid for c in credexs])
        else:
            pmexs = await models.PmEx.filter(ex=self.actor.ex, pm__pmcurs__id__in=[cx.cred.pmcur_id for cx in credexs])
            ad_ein = AdMakerNewBuy(**ad_ein.model_dump(exclude_none=True), paymentMethodCodes=[p.exid for p in pmexs])
        return ad_ein

    # 30: Создание объявления
    async def ad_new(self, ad: _AdNew) -> OneAdMakerBuy | OneAdTakerMakerSale:
        create = await self._post("/p2p/public-api/v2/offer/create", ad.model_dump())
        if res := create.get("data"):
            return OneAdTakerMakerSale(**res) if res["type"] == "SALE" else OneAdMakerBuy(**res)
        raise Exception(create)

    # 31: Редактирование объявления
    async def ad_upd(
        self,
        offer_id: int,
        amount: int,
        creds: list[models.Cred] = None,
        price: float = None,
        is_float: bool = None,
        min_fiat: int = None,
        details: str = None,
        autoreply: str = None,
        status: AdStatus = None,
    ) -> object:
        ad = await self.my_ad(offer_id)

        upd = await self._post(
            "/p2p/public-api/v2/offer/edit",
            {
                "offerId": offer_id,
                "paymentConfirmTimeout": ad["paymentConfirmTimeout"],
                "type": ad["type"],
                "orderRoundingRequired": False,
                "price": {"type": "FIXED", "value": ad["price"]["value"]},
                "orderAmountLimits": {"min": ad["orderAmountLimits"]["min"]},
                "comment": "",  # TODO: comment
                "volume": f"{amount}",
                "paymentDetailsIds": [a["id"] for a in ad["paymentDetails"]],
            },
        )
        return upd

    # 32: Удаление
    async def ad_del(self, offer_id: int) -> bool:
        ad = await self.my_ad(offer_id)
        ad_del = await self._post("/p2p/public-api/v2/offer/delete", {"type": ad["type"], "offerId": offer_id})
        return ad_del["status"] == "SUCCESS"

    # 33: Вкл/выкл объявления
    async def ad_switch(self, ad_id: int, active: bool) -> bool:
        ad: OneAdMakerBuy | OneAdTakerMakerSale = await self.my_ad(ad_id)
        pre = "" if active else "de"
        switch = await self._post(f"/p2p/public-api/v2/offer/{pre}activate", {"type": ad.type, "offerId": ad_id})
        return switch["status"] == "SUCCESS"

    # 34: Вкл/выкл всех объявлений
    async def ads_switch(self, active: bool) -> bool:
        pre = "enable" if active else "disable"
        switch = await self._post(f"/p2p/public-api/v2/user-settings/{pre}-bidding")
        return switch["status"] == "SUCCESS"

    # 35: Получить объект юзера по его ид
    async def get_user(self, user_id: int = None, offer_id: int = None) -> dict:
        user = await self._post("/p2p/public-api/v2/offer/get", {"offerId": offer_id})
        return user["data"]["user"]

    # 36: Отправка сообщения юзеру с приложенным файлом
    async def send_user_msg(self, msg: str, file=None) -> bool:
        pass

    # 37: (Раз)Блокировать юзера
    async def block_user(self, is_blocked: bool = True) -> bool:
        return None

    # 38: Поставить отзыв юзеру
    async def rate_user(self, positive: bool) -> bool:
        return None

    # base_url = 'https://p2p.walletbot.me'
    # middle_url = '/p2p/'

    # 19 - order_paid
    async def order_paid(self, order_id: str, file: dict):
        paid = await self._post(
            "/p2p/public-api/v2/offer/order/confirm-sending-payment", {"orderId": order_id, "paymentReceipt": file}
        )
        return paid


async def main():
    await init_db(PG_DSN, models, True)
    # pm = await models.Pm.first()
    # pm_in = models.Pm.validate(dict(pm))
    # await models.Pm.update_or_create(**pm_in.df_unq())
    # user = await models.User.first()
    # user_in = models.User.validate(dict(user))
    # await models.User.update_or_create(**user_in.df_unq())
    # cred = await models.Cred.first()
    # cred_in = models.Cred.validate(dict(cred))
    # await models.Cred.update_or_create(**cred_in.df_unq())
    maker: models.Actor
    taker: models.Actor
    maker, taker = (
        await models.Actor.filter(ex_id=34, agent__isnull=False, person__user__status__gt=UserStatus.SLEEP)
        # .order_by("-my_ads")
        .limit(2)
        .prefetch_related("ex", "agent", "person__user")
    )
    mcl: AgentClient = maker.client()
    tcl: AgentClient = taker.client()
    # await mcl.set_creds()
    # await tcl.set_creds()
    # my_ads = await tcl.my_ads()
    # my_ads_in = [await tcl.ad_epyd2pydin(ma) for ma in my_ads]
    # _my_ads_db = [await tcl.ex_client.ad_pydin2db(ma) for ma in my_ads_in]

    coin = await models.Coin.get(ticker="USDT")
    cur = await models.Cur.get(ticker="RUB")
    ad_sell_ein = await tcl.ad_f2ein(coin, cur, True)
    ad_buy_ein = await mcl.ad_f2ein(coin, cur, False)
    sad = await tcl.ad_new(ad_sell_ein)
    bad = await mcl.ad_new(ad_buy_ein)
    await tcl.ad_switch(sad.id, True)
    await mcl.ad_switch(bad.id, True)
    sad_in = await tcl.ad_epyd2pydin(sad)
    sad_db = await models.Ad.create(**sad_in.model_dump(exclude_none=True))
    bad_in = await mcl.ad_epyd2pydin(bad)
    await models.Ad.create(**bad_in.model_dump(exclude_none=True))

    order_epin: OrderReqTrait = await tcl.order_ad2epydin(sad_db, float(sad.orderAmountLimits.min))
    new_order: OrderEpyd = await tcl.order_request(order_epin)
    order_pin: OrderIn = await tcl.order_epyd2pydin(new_order)
    _order_db = await tcl.order_pydin2db(order_pin)

    # order_epin: OrderEpydIn = await tcl.order_ad2epydin(ad_db, float(mad.orderAmountLimits.min), cred_ids[0])
    # new_order: OrderEpyd = await tcl.order_request(order_epin)
    # order_pin: OrderIn = await tcl.order_epyd2pydin(new_order)
    # _order_db = await tcl.order_pydin2db(order_pin)

    await tcl.close(), await mcl.close()


if __name__ == "__main__":
    run(main())
