# from asyncio import AbstractEventLoop
#
# import pytest
# import uvloop
# from xync_schema.models import ExAction, ExStat
#
#
# @pytest.mark.asyncio(loop_scope="class")
# class TestWallet:
#     loop: AbstractEventLoop
#
#     @pytest.fixture(scope="class")
#     def event_loop_policy(self):
#         return uvloop.EventLoopPolicy()
#
#     # 20 - all_pms
#     async def test_all_pms(self, cl):
#         pms = await cl.pms()
#         pms and cl.is_pms(pms)
#         test, _ = await ExStat.update_or_create({"ok": bool(pms)}, ex=cl.ex, action=ExAction.pms)
#         assert test.ok, "No pms"
#
#     # 21 - all_curs
#     async def test_all_curs(self, cl):
#         curs = await cl.curs()
#         test, _ = await ExStat.update_or_create({"ok": bool(curs)}, ex=cl.ex, action=ExAction.curs)
#         assert test.ok, "No curs"
#
#     # 22 - all_pms
#     async def test_cur_pms_map(self, cl):
#         pms = await cl.cur_pms_map()
#         test, _ = await ExStat.update_or_create({"ok": bool(pms)}, ex=cl.ex, action=ExAction.pms)
#         assert test.ok, "No pms"
#
#     # 23 - all_coins
#     async def test_all_coins(self, cl):
#         coins = await cl.coins()
#         test, _ = await ExStat.update_or_create({"ok": bool(coins)}, ex=cl.ex, action=ExAction.coins)
#         assert test.ok, "No coins"
#
#     # 24 - all_ads
#     async def test_cur_filter(self, cl):
#         for cur in "RUB", "AZN", "GEL":
#             for coin in "TON", "USDT", "BTC":
#                 for tt in True, False:
#                     ads = await cl.ads(coin, cur, tt)
#                     assert len(ads), "No data"
#         await ExStat.update_or_create({"ok": bool(ads)}, ex=cl.ex, action=ExAction.ads)
