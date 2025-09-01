# from xync_client.Gate.premarket import Priv
# from xync_client.loader import GATE_UID, GATE_PVER
#
#
# async def test_get_premarket_ads():
#     gate = Priv(GATE_UID, GATE_PVER)
#     resp = await gate.get_premarket_ads()
#     assert len(resp), "No premarket ads"
#
#
# async def test_get_my_premarket_ads():
#     gate = Priv(GATE_UID, GATE_PVER)
#     resp = await gate.get_my_premarket_ads()
#     assert len(resp), "No my premarket ads"
#
#
# async def test_create_premarket_ad():
#     gate = Priv(GATE_UID, GATE_PVER)
#     resp = await gate.post_premarket_ad(0.649, 5)
#     assert resp, "Premarket ad not created"
#
#
# async def test_delate_premarket_ad():
#     gate = Priv(GATE_UID, GATE_PVER)
#     resp = await gate.del_premarket_ad(62089)
#     assert resp, "Premarket ad not delated"
#
#
# async def test_set_premarket_ads():
#     gate = Priv(GATE_UID, GATE_PVER)
#     my_ads = await gate.get_my_premarket_ads()
#     my_ids = [ad["order_id"] for ad in my_ads]
#     resp = await gate.get_premarket_ads()
#     for ad in resp:
#         if ad["order_id"] in my_ids:
#             pass
#
#     assert len(resp), "No premarket ads"
