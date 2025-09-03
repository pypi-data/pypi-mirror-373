import logging

import pytest
from pyro_client.client.file import FileClient
from x_client.aiohttp import Client as HttpClient
from xync_schema.xtype import BaseAd

from xync_client.Abc.BaseTest import BaseTest
from xync_schema.enums import ExStatus, ExType, ExAction
from xync_schema import models
from xync_client.Abc.Ex import BaseExClient
from xync_client.loader import TOKEN


@pytest.mark.asyncio(loop_scope="session")
class TestEx(BaseTest):
    @pytest.fixture
    async def clients(self) -> list[HttpClient]:
        exs = await models.Ex.filter(status__gt=ExStatus.plan).prefetch_related("pm_reps")
        [await ex for ex in exs if ex.typ == ExType.tg]
        async with FileClient(TOKEN) as b:
            b: FileClient
            clients: list[BaseExClient] = [ex.client(b) for ex in exs]
            yield clients
        [await cl.close() for cl in clients]

    # 0
    async def test_set_coins(self, clients: list[BaseExClient]):
        for client in clients:
            await client.set_coins()
            t, _ = await models.ExStat.update_or_create({"ok": True}, ex=client.ex, action=ExAction.set_coins)
            assert t.ok, "Coins not set"
            logging.info(f"{client.ex.name}: {ExAction.set_coins.name} - ok")

    # 0
    async def test_set_curs(self, clients: list[BaseExClient]):
        for client in clients:
            await client.set_curs()
            t, _ = await models.ExStat.update_or_create({"ok": True}, ex=client.ex, action=ExAction.set_curs)
            assert t.ok, "Curs not set"
            logging.info(f"{client.ex.name}: {ExAction.set_curs.name} - ok")

    # 0
    async def test_set_pms(self, clients: list[BaseExClient]):
        for client in clients:
            await client.set_pms()
            t, _ = await models.ExStat.update_or_create({"ok": True}, ex=client.ex, action=ExAction.set_pms)
            assert t.ok, "Pms not set"
            logging.info(f"{client.ex.name}: {ExAction.set_pms.name} - ok")

    # 0
    async def test_set_pairs(self, clients: list[BaseExClient]):
        for client in clients:
            await client.set_pairs()
            t, _ = await models.ExStat.update_or_create({"ok": True}, ex=client.ex, action=ExAction.set_pairs)
            assert t.ok, "Pairs not set"
            logging.info(f"{client.ex.name}: {ExAction.set_pairs.name} - ok")

    # # 19
    # async def test_curs(self, clients: list[BaseExClient]):
    #     for client in clients:
    #         curs: dict[str, CurEx] = await client.curs()
    #         ok = self.is_dict_of_objects(curs, CurEx)
    #         t, _ = await ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.curs)
    #         assert t.ok, "No curs"
    #         logging.info(f"{client.ex.name}: {ExAction.curs.name} - ok")
    #
    # # 20
    # async def test_pms(self, clients: list[BaseExClient]):
    #     for client in clients:
    #         pms: dict[int | str, PmEx] = await client.pms()
    #         ok = self.is_dict_of_objects(pms, PmEx)
    #         t, _ = await ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.pms)
    #         assert t.ok, "No pms"
    #         logging.info(f"{client.ex.name}: {ExAction.pms.name} - ok")
    #
    # # 21
    # async def test_cur_pms_map(self, clients: list[BaseExClient]):
    #     for client in clients:
    #         cur_pms: MapOfIdsList = await client.cur_pms_map()
    #         ok = self.is_map_of_ids(cur_pms)
    #         t, _ = await ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.cur_pms_map)
    #         assert t.ok, "No pms for cur"
    #         logging.info(f"{client.ex.name}: {ExAction.cur_pms_map.name} - ok")

    # 22
    # async def test_coins(self, clients: list[BaseExClient]):
    #     for client in clients:
    #         coins: dict[str, CoinEx] = await client.coins()
    #         ok = self.is_dict_of_objects(coins, CoinEx)
    #         t, _ = await ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.coins)
    #         assert t.ok, "No coins"
    #         logging.info(f"{client.ex.name}: {ExAction.coins.name} - ok")

    # # 23
    # async def test_pairs(self, clients: list[BaseExClient]):
    #     for client in clients:
    #         pairs_buy, pairs_sell = await client.pairs()
    #         ok = self.is_map_of_ids(pairs_buy) and self.is_map_of_ids(pairs_sell)
    #         t, _ = await ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.pairs)
    #         assert t.ok, "No coins"
    #         logging.info(f"{client.ex.name}: {ExAction.pairs.name} - ok")

    # 24
    async def test_ads(self, clients: list[BaseExClient]):
        for client in clients:
            cur = await models.CurEx.filter(cur__ticker="EUR", ex=client.ex).first().values_list("exid", flat=True)
            coin = await models.CoinEx.filter(coin__ticker="USDT", ex=client.ex).first().values_list("exid", flat=True)
            ads: list[BaseAd] = await client.ads(coin, cur, False)
            ok = self.is_list_of_objects(ads, BaseAd)
            t, _ = await models.ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.ads)
            assert t.ok, "No ads"
            logging.info(f"{client.ex.name}: {ExAction.ads.name} - ok")

    async def test_race(self, clients: list[BaseExClient]):
        races: list[models.Race] = await models.Race.filter(started=True).prefetch_related(
            "road__ad__pair_side__pair", "road__ad__maker", "road__ad__pms"
        )
        ex_ids: set = {race.road.ad.maker.ex_id for race in races}
        errors: dict[int, int | None] = {}
        for client in clients:
            if client.ex.id not in ex_ids:
                continue
            for race in races:
                # получаем данные направления текущей гонки
                coinex = await models.CoinEx.get(ex=client.ex, coin_id=race.road.ad.pair_side.pair.coin_id)
                curex = await models.CurEx.get(ex=client.ex, cur_id=race.road.ad.pair_side.pair.cur_id)
                pm_ids = [pm.id for pm in race.road.ad.pms]
                pmex_exids = await models.PmEx.filter(ex=client.ex, pm_id__in=pm_ids).values_list("exid", flat=True)
                # получаем объявления по этому направлению
                ads = await client.ads(coinex.exid, curex.exid, race.road.ad.pair_side.is_sell, pmex_exids)
                # if race.vm_filter:
                #     ads = [ad for ad in ads if "VA" in ad.authTag]
                # client.overprice_filter(ads, race.ceil, k)  # обрезаем сверху все ads дороже нашего потолка
                # определяем место нашего объявления в списке
                places = [i for i, ad in enumerate(ads) if int(ad.userId) == race.road.ad.maker.exid]
                if not places:
                    errors[race.id] = None
                elif places[0] != race.target_place:
                    errors[race.id] = places[0]
        assert not errors, "Гонка " + ", ".join(f"#{rid} на {plc} месте" for rid, plc in errors.items())
