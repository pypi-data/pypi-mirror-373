# from datetime import datetime
# from uuid import uuid4
# from pybit.unified_trading import HTTP
#
# from xync_client.Bybit.web_earn import BybitEarn, type_map
# from xync_client.loader import BYT, BYKEY, BYSEC
#
# client = HTTP(
#     testnet=False,
#     api_key=BYKEY,
#     api_secret=BYSEC,
# )
#
#
# async def test_get_home_products():
#     bbt = BybitEarn(BYT)
#     for pt in type_map:
#         resp = await bbt.get_home_earn_products(pt.value)
#         assert len(resp[pt.name]), "No home products"
#
#
# async def test_get_coins():
#     bbt = BybitEarn(BYT)
#     resp = await bbt.get_coins()
#     assert resp, "No coins"
#
#
# async def test_get_eth():
#     bbt = BybitEarn(BYT)
#     resp = await bbt.get_product_detail()
#     assert resp, "No eth"
#
#
# def test_get_rate():
#     resp = client.get_tickers(category="spot", symbol="TONUSDT")
#     assert float(resp["result"]["list"][0]["lastPrice"]) > 0
#
#
# def test_send_coin_internal():
#     coin = "USDT"
#     old_sender_balance = client.get_coins_balance(
#         accountType="FUND",
#         coin=coin,
#     )["result"]["balance"][0]
#     # sender_id = 23477628
#     # receiver_id = 138687729
#     receiver_id = 69798104
#     sent_amount = 24.9266
#     assert float(old_sender_balance["transferBalance"]) >= sent_amount, "sender have not enough money"
#
#     trans_sent_id = client.withdraw(
#         coin=coin,
#         # chain=None,
#         address=str(receiver_id),
#         amount=str(sent_amount),
#         timestamp=int(datetime.now().timestamp() * 1000),
#         forceChain=2,
#         accountType="FUND",
#     )["result"]
#     new_sender_balance = client.get_coins_balance(
#         accountType="FUND",
#         coin=coin,
#     )["result"]["balance"][0]
#     assert (
#         trans_sent_id
#         and float(new_sender_balance["walletBalance"]) == float(old_sender_balance["walletBalance"]) - sent_amount
#     ), "transfer failed"
#
#
# def test_send_coin_subaccount():
#     sender_id = 23477628
#     receiver_id = 69798104
#     sent_amount = 15.5
#     sent = client.create_universal_transfer(  # its only for subaccount transfers
#         transferId=str(uuid4()),
#         coin="USDT",
#         amount=str(sent_amount),
#         fromMemberId=sender_id,
#         toMemberId=receiver_id,
#         fromAccountType="FUND",
#         toAccountType="FUND",
#     )["result"]
#     assert sent, "transfer failed"
