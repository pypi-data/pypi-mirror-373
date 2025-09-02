from x_client.aiohttp import Client


class Priv(Client):
    host = "www.gate.io"

    def __init__(self, uid: str, pver: str):
        self.headers = {
            # 'content-type': 'application/json',
            "cookie": f"uid={uid};pver={pver}"
        }
        super().__init__()

    # 1: Get ads for taker
    async def get_premarket_ads(
        self, cur: str = "HMSTR", sell: bool = True, done: bool = False, limit: int = 100
    ) -> list[dict]:
        params = {
            "page": 1,
            "limit": limit,
            "currency": cur,
            "side": "sell" if sell else "buy",
            "status": "transaction_completed" if done else "no_transaction",
        }
        res = await self._get("/apiw/v2/pre_market/market_orders", params)
        return res["data"]["list"]

    # 2: Get my ads
    async def get_my_premarket_ads(self) -> list[dict]:
        params = {"type": "current_orders", "page": 1, "limit": 100}
        res = await self._get("/apiw/v2/pre_market/orders", params)
        return res["data"]["list"]

    # 3: New ad
    async def post_premarket_ad(self, price: float, amount: int, sell: bool = True, cur: str = "HMSTR") -> int:
        data = {
            "fundpass": "",
            "currency": cur,
            "side": "sell" if sell else "buy",
            "amount": str(amount),
            "price": str(price),
        }
        res = await self._post("/apiw/v2/pre_market/orders", data)
        return res["data"]["order_id"]

    # 4: Del ad
    async def del_premarket_ad(self, order_id: int) -> bool:
        res = await self._delete(f"/apiw/v2/pre_market/orders/{order_id}")
        return not res["code"]

    # 5: Execute deal
    async def deal(self, order_id: int, price: float, amount: int, sell: bool = True, cur: str = "HMSTR") -> bool:
        data = {
            "fundpass": "",
            "currency": cur,
            "side": "sell" if sell else "buy",
            "amount": amount,
            "price": price,
            "deal_order_id": order_id,
        }
        res = await self._post("/apiw/v2/pre_market/deal_order", data)
        return not res["code"]
