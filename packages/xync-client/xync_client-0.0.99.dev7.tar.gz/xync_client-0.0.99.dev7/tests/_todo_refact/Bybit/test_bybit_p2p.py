# from time import sleep
#
# import pytest
# from tortoise import Tortoise, connections
# from tortoise.backends.asyncpg import AsyncpgDBClient
# from xync_schema import models
# from xync_schema.models import ExStat, ExAction
#
# from xync_client.Bybit.web_p2p import BybitP2P, NoMakerException, AdsStatus
# from xync_client.loader import BYTP2P, PG_DSN
#
# bybit_p2p = BybitP2P(headers={"cookie": "secure-token=" + BYTP2P})
#
#
# @pytest.fixture(scope="module")
# async def dbc() -> AsyncpgDBClient:
#     await Tortoise.init(db_url=PG_DSN, modules={"models": [models]})
#     cn: AsyncpgDBClient = connections.get("default")
#     yield cn
#     await cn.close()
#
#
# # получение валют (1)
# async def test_get_currencies(dbc):
#     currencies = bybit_p2p.get_currencies()
#     ok = True if len(currencies) > 0 else False
#     await ExStat.update_or_create({"ok": ok}, ex_id=10, action=ExAction.curs)
#     assert ok, "No currencies found"
#
#
# # получение не тестовых монет торгуемых на p2p (2)
# async def test_get_coins(dbc):
#     result_get_coins = bybit_p2p.get_coins()
#     ok = (
#         True
#         if len([c for c in result_get_coins["result"] if c["tokenType"] == "CHAIN_TOKEN" and not c["isTest"]]) > 0
#         else False
#     )
#     await ExStat.update_or_create({"ok": ok}, ex_id=10, action=ExAction.coins)
#     assert ok, "No coins found"
#
#
# # получение платежных методов (3)
# async def test_get_payment_methods(dbc):
#     result_get_payment_methods = bybit_p2p.get_payment_methods()
#     ok = True if len(result_get_payment_methods["result"]["paymentConfigVo"]) > 0 else False
#     await ExStat.update_or_create({"ok": ok}, ex_id=10, action=ExAction.pms)
#     assert ok, "No payment method found"
#
#
# # получение первого объявления на покупку USDT за рубли (покупка - "side": "1", продажа - "side": "0") (4)
# async def test_get_best_price(dbc):
#     all_ads = bybit_p2p.get_ads("USDT", "RUB")
#     ok1 = True if bybit_p2p.get_rate(all_ads) > 0 else False  # "Ad's price USDT/RUB no found no Payeer, no Advcash"
#     ok2 = True if len(all_ads) > 0 else False
#     await ExStat.update_or_create({"ok": ok1 and ok2}, ex_id=10, action=ExAction.ads)
#     assert ok2, "Ad's price USDT/RUB no found"
#
#
# # получение платежных методов залогиненного юзера (5)
# async def test_get_user_pay_methods(dbc):
#     result_get_user_pay_methods = bybit_p2p.get_user_pay_methods()
#     ok = True if len(result_get_user_pay_methods) > 0 else False
#     await ExStat.update_or_create({"ok": ok}, ex_id=10, action=ExAction.my_fiats)
#     assert ok, "No payment method requisites found"
#
#
# # создание моего платежного реквизита (fiat) (6)
# async def test_create_user_payment_methods(dbc):
#     result = bybit_p2p.create_payment_method(379, "ЕЛЕНА АРТЕМЬЕВА", "42454342536453")
#     ok = True if result["ret_msg"] == "SUCCESS" else False
#     await ExStat.update_or_create({"ok": ok}, ex_id=10, action=ExAction.fiat_new)
#     assert ok, "Fiat isn't created: " + result["ret_msg"]
#
#
# # редактирование моего платежного реквизита (fiat) (7)
# async def test_update_user_payment_methods(dbc):
#     result = bybit_p2p.update_payment_method("ЕЛЕНА АРТЕМЬЕВА", "424543425364532")
#     if result["ret_msg"] != "SUCCESS":
#         print("Wrong 2fa on Fiat updating, wait 10 secs and retry..")
#         sleep(10)
#         return await test_update_user_payment_methods(dbc)
#     await ExStat.update_or_create({"ok": True}, ex_id=10, action=ExAction.fiat_upd)
#     assert True, "Fiat isn't updated: " + result["ret_msg"]
#
#
# # удаление моего платежного реквизита (fiat) (8)
# async def test_delete_user_payment_methods(dbc):
#     last_fiat = bybit_p2p.get_payment_method()
#     result = bybit_p2p.delete_payment_method(last_fiat["id"])
#     if result["ret_msg"] != "SUCCESS":
#         print("Wrong 2fa on Fiat deleting, wait 10 secs and retry..")
#         sleep(10)
#         return await test_delete_user_payment_methods(dbc)
#     await ExStat.update_or_create({"ok": True}, ex_id=10, action=ExAction.fiat_del)
#     assert True, "Fiat isn't deleted: " + result["ret_msg"]
#
#
# # получение списка объявлений залогиненного юзера (9)
# async def test_get_user_ads(dbc):
#     result_get_user_ads = bybit_p2p.get_user_ads()
#     ok = True if len(result_get_user_ads) >= 0 else False
#     await ExStat.update_or_create({"ok": ok}, ex_id=10, action=ExAction.my_ads)
#     assert ok, "No ads found"
#
#
# # создание/редактирование/удаление объявления (10,11,12)
# async def test_delete_ad(dbc):
#     try:
#         token = bybit_p2p.get_security_token_create()
#         bybit_p2p.post_create_ad(token)
#         token = bybit_p2p.get_security_token_update()
#         bybit_p2p.post_update_ad(token)
#         result_delete_ad = bybit_p2p.delete_ad(bybit_p2p.last_ad_id[0])
#     except NoMakerException as e:
#         print(e.args[0]["ret_msg"])
#         result_delete_ad = e.args[0]
#     ok = True if result_delete_ad["ret_msg"] == "SUCCESS" else False
#     await ExStat.update_or_create({"ok": ok}, ex_id=10, action=ExAction.ad_new)
#     await ExStat.update_or_create({"ok": ok}, ex_id=10, action=ExAction.ad_upd)
#     await ExStat.update_or_create({"ok": ok}, ex_id=10, action=ExAction.ad_del)
#     assert ok, "Ad isn't deleted"
#
#
# async def _switch_ad(new_status: AdsStatus):
#     result = bybit_p2p.switch_ads(new_status)
#     ok = True if result["ret_msg"] == "SUCCESS" else False
#     action = {AdsStatus.REST: ExAction.ad_switch, AdsStatus.WORKING: ExAction.ad_switch}[new_status]
#     await ExStat.update_or_create({"ok": ok}, ex_id=10, action=action)
#     return ok
#
#
# # выключение/включение объявления (13,14)
# async def test_on_off_ads(dbc):
#     old_status = AdsStatus[bybit_p2p.online_ads()]
#     new_status = AdsStatus(int(not bool(old_status.name)))
#     ok = await _switch_ad(new_status)
#     assert ok, "Ad no " + new_status.name
#     # возвращаем как было:
#     ok = await _switch_ad(old_status)
#     assert ok, "Ad no " + old_status.name
#
#
# # старт заявки (тейкером 17)
# async def test_create_order_taker():
#     ads = bybit_p2p.get_ads("USDT", "RUB", payment=["51"])
#     ad = ads[0]
#     # get_order_info = bybit_p2p.get_order_info(ad["id"])
#     result = bybit_p2p.create_order_taker(
#         ad["id"], "USDT", "RUB", False, ad["minAmount"], float(ad["minAmount"]) / float(ad["price"]), ad["price"]
#     )
#     ok = True if result["ret_msg"] == "SUCCESS" else False
#     await ExStat.update_or_create({"ok": ok}, ex_id=10, action=ExAction.order_request)
#
#
# # сообщения чата (тейкером 21)
# async def test_get_chat_msgs(dbc):
#     msgs = bybit_p2p.get_chat_msg("1832490804709646336")
#     assert len(msgs) > 0, "No have msgs"
#
#
# async def test_user_block(dbc):
#     bu = bybit_p2p.block_user("146246740")
#     assert bu["result"], "User don't block"
#     ubu = bybit_p2p.unblock_user("146246740")
#     assert ubu["result"], "User don't unblock"
#
#
# # поставить отзыв (27)
# async def test_user_review_post(dbc):
#     result = bybit_p2p.user_review_post("1831422797854318592")
#     assert result["ret_msg"] == "SUCCESS", "Review post failed"
#
#
# # получшение заявок по всем ордерам за заданное время, статус, направление, монета (32)
# async def test_get_orders_done(dbc):
#     result = bybit_p2p.get_orders_done(1717189200000, 1722545999999, 50, 1, "USDT")
#     assert result["ret_msg"] == "SUCCESS", "No orders done"
#
#
# # получшение заявок по активным ордерам за заданное время, статус, направление, монета (32)
# async def test_get_orders_active(dbc):
#     result = bybit_p2p.get_orders_active(1717189200000, 1722545999999, 50, 1, "USDT")
#     assert result["ret_msg"] == "SUCCESS", "No active orders"
#
#
# # 33
# async def test_get_order_info(dbc):
#     get_order_info = bybit_p2p.get_order_info("1819108572048125952")
#     assert get_order_info, "No order info"
