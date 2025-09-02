import logging

import pytest
from tortoise.functions import Count
from xync_schema.enums import ExStatus, ExAction, UserStatus
from xync_schema.models import Ex, ExStat, Ad, Coin, Cur, PmCur, Cred, CredEx, Actor, Person
from xync_schema.xtype import BaseAd

from xync_client.Abc.BaseTest import BaseTest
from xync_client.Abc.Ex import BaseExClient
from xync_client.Abc.Agent import BaseAgentClient
from xync_client.Abc.xtype import CredExOut, BaseOrderReq, ListOfDicts


@pytest.mark.asyncio(loop_scope="session")
class TestAgent(BaseTest):
    @pytest.fixture(scope="class", autouse=True)
    async def clients(self) -> list[tuple[BaseAgentClient, BaseAgentClient]]:
        exs = await Ex.annotate(agents=Count("actors")).filter(status__gt=ExStatus.plan, agents__gt=1)
        actors: list[list[Actor]] = [
            await ex.actors.filter(person__user__status__gt=UserStatus.SLEEP)
            .annotate(ads=Count("my_ads"))
            .order_by("-ads")
            .prefetch_related("ex", "agent", "person__user")
            .limit(2)
            for ex in exs
        ]
        clients: list[tuple[BaseAgentClient, BaseAgentClient]] = [(m.client(), t.client()) for m, t in actors]
        yield clients
        [(await maker.close(), await taker.close()) for maker, taker in clients]

    # 26
    async def test_cred_new(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            pmcur = await PmCur.filter(pm__pmexs__ex=taker.actor.ex, cur__ticker="RUB", pm__norm="payeer").first()
            cred = await Cred.create(person_id=taker.actor.person_id, name="Tst", detail="79990001234", pmcur=pmcur)
            # await cred.banks.add(await PmExBank.get(exid="mts"), await PmExBank.get(exid="sberbankru"))
            cred_new: CredEx = await taker.cred_new(cred)
            ok = isinstance(cred_new, CredEx)
            t, _ = await ExStat.update_or_create({"ok": ok}, ex=taker.actor.ex, action=ExAction.cred_new)
            assert t.ok, "No add cred"
            logging.info(f"{taker.actor.ex.name}:{ExAction.cred_new.name} - ok")

    # 25
    async def test_my_creds(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            my_creds: list[CredExOut] = await taker.creds()
            ok = self.is_list_of_objects(my_creds, CredExOut)
            t, _ = await ExStat.update_or_create({"ok": ok}, ex=taker.actor.ex, action=ExAction.my_creds)
            assert t.ok, "No my creds"
            logging.info(f"{taker.actor.ex.name}:{ExAction.my_creds.name} - ok")

    # 27
    async def test_cred_upd(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            credex = (await taker.creds())[0]
            credex_db = await CredEx.get(exid=credex.id, ex=taker.actor.ex).prefetch_related("cred")
            credex_db.cred.name += "+Test!"
            cred_upd: CredEx = await taker.cred_upd(credex_db.cred, credex.id)
            ok = isinstance(cred_upd, CredEx)
            t, _ = await ExStat.update_or_create({"ok": ok}, ex=taker.actor.ex, action=ExAction.cred_upd)
            assert t.ok, "No upd cred"
            logging.info(f"{taker.actor.ex.name}:{ExAction.cred_upd.name} - ok")

    # 28
    async def test_cred_del(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            credex = (await taker.creds())[0]
            cred_del: int = await taker.cred_del(credex.id)
            ok = cred_del == credex.id
            t, _ = await ExStat.update_or_create({"ok": ok}, ex=taker.actor.ex, action=ExAction.cred_del)
            assert t.ok, "No del cred"
            logging.info(f"{taker.actor.ex.name}:{ExAction.cred_del.name} - ok")

    # 42
    async def test_ad(self, clients: list[BaseExClient]):
        for client in clients:
            if not self.ad.get(client.ex.id):
                await self.test_ads(clients)
            ad: BaseAd = await client.ad(self.ad[client.ex.id].id)
            ok = isinstance(ad, BaseAd)
            t, _ = await ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.ad)
            assert t.ok, "No ad"
            logging.info(f"{client.ex.name}: {ExAction.ad.name} - ok")

    # 0
    async def test_get_orders(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            get_orders: ListOfDicts = await taker.get_orders()
            ok = self.is_list_of_dicts(get_orders, False)
            t, _ = await ExStat.update_or_create({"ok": ok}, ex=taker.actor.ex, action=ExAction.get_orders)
            assert t.ok, "No get orders"
            logging.info(f"{taker.actor.ex.name}:{ExAction.get_orders.name} - ok")

    # 1
    async def test_order_request(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            ad = (
                await Ad.filter(
                    maker=maker.actor,
                    direction__pairex__ex=maker.ex,
                    direction__sell=True,
                    direction__pairex__pair__cur__ticker="RUB",
                    direction__pairex__pair__coin__ticker="USDT",
                )
                .prefetch_related("direction", "creds")
                .first()
            )
            pers: Person = taker.actor.person
            mutual_cred: Cred = await pers.creds.filter(pmcur_id__in=[c.pmcur_id for c in ad.creds]).first()
            req = BaseOrderReq(
                ad_id=ad.exid,
                is_sell=ad.direction.sell,
                fiat_amount=ad.min_fiat,
                cred_id=mutual_cred.id,
            )
            order_request: dict | bool = await taker.order_request(req)
            ok = order_request["status"] == "SUCCESS"
            t, _ = await ExStat.update_or_create({"ok": ok}, ex=taker.actor.ex, action=ExAction.order_request)
            assert t.ok, "No get orders"
            logging.info(f"{taker.actor.ex.name}:{ExAction.order_request.name} - ok")

    # 29
    async def test_my_ads(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            my_ads: list[BaseAd] = await maker.my_ads()
            ok = self.is_list_of_objects(my_ads, BaseAd)
            t, _ = await ExStat.update_or_create({"ok": ok}, ex=taker.actor.ex, action=ExAction.my_ads)
            assert t.ok, "Maker should has ads"
            logging.info(f"{taker.actor.ex.name}:{ExAction.my_ads.name} - ok")

    # 30
    async def test_ad_new(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            my_creds = await taker.my_creds()
            my_cred = list(my_creds.values())[0]
            coin = await Coin.get(ticker="USDT")
            cur = await Cur.get(ticker=my_cred["currency"])
            # pm = await Fiatex.get()
            ad_new: Ad.pyd() = await taker.ad_new(
                coin=coin, cur=cur, is_sell=True, creds=[my_cred["id"]], amount="10", price="120", min_cred="500"
            )
            ok = ad_new["status"] == "SUCCESS"
            t, _ = await ExStat.update_or_create({"ok": ok}, ex=taker.actor.ex.name, action=ExAction.ad_new)
            assert t.ok, "No add new ad"
            logging.info(f"{taker.actor.ex.name}:{ExAction.ad_new.name} - ok")

    # 31
    async def test_ad_upd(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            my_ads: ListOfDicts = await taker.my_ads()
            ad_upd: Ad.pyd() = await taker.ad_upd(offer_id=my_ads[0]["id"], amount="11")
            ok = ad_upd["status"] == "SUCCESS"
            t, _ = await ExStat.update_or_create({"ok": ok}, ex=taker.actor.ex.name, action=ExAction.ad_upd)
            assert t.ok, "No add new ad"
            logging.info(f"{taker.actor.ex.name}:{ExAction.ad_upd.name} - ok")

    # 32
    async def test_ad_del(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            my_ads: ListOfDicts = await taker.my_ads()
            ad_del: bool = await taker.ad_del(ad_id=my_ads[0]["id"])
            t, _ = await ExStat.update_or_create({"ok": ad_del}, ex=taker.actor.ex, action=ExAction.ad_del)
            assert t.ok, "No add new ad"
            logging.info(f"{taker.actor.ex.name}:{ExAction.ad_del.name} - ok")

    # 33
    async def test_ad_switch(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            my_ads: ListOfDicts = await taker.my_ads()
            new_status = not (my_ads[0]["status"] == "ACTIVE")
            ad_switch: bool = await taker.ad_switch(offer_id=my_ads[0]["id"], active=new_status)
            t, _ = await ExStat.update_or_create({"ok": ad_switch}, ex=taker.actor.ex, action=ExAction.ad_switch)
            assert t.ok, "No ad active/off"
            logging.info(f"{taker.actor.ex.name}:{ExAction.ad_switch.name} - ok")

    # 34
    async def test_ads_switch(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            ads_switch: bool = await taker.ads_switch(active=False)
            t, _ = await ExStat.update_or_create({"ok": ads_switch}, ex=taker.actor.ex, action=ExAction.ads_switch)
            assert t.ok, "No ads switch"
            logging.info(f"{taker.actor.ex.name}:{ExAction.ads_switch.name} - ok")

    # 35
    async def test_get_user(self, clients: list[tuple[BaseAgentClient, BaseAgentClient]]):
        for maker, taker in clients:
            await taker.actor.fetch_related("ex", "ex__agents")
            ex_client: BaseExClient = taker.actor.ex.client()
            ads = await ex_client.ads("NOT", "RUB", False)
            user_info = await taker.get_user(offer_id=ads[0]["id"])
            ok = isinstance(user_info, dict) and user_info
            t, _ = await ExStat.update_or_create({"ok": ok}, ex=taker.actor.ex, action=ExAction.get_user)
            assert t.ok, "No get user information"
            logging.info(f"{taker.actor.ex.name}:{ExAction.get_user.name} - ok")
