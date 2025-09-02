import json
import subprocess
from asyncio import run
from x_model import init_db
from xync_schema import models
from xync_schema.enums import AdStatus, PmType, OrderStatus
from xync_schema.models import User, Pm, Coin, Cur, Ad, Fiat, Order, Agent
from xync_schema.pydantic import FiatNew

from xync_client.Abc.Agent import BaseAgentClient
from xync_client.loader import PG_DSN


class Client(BaseAgentClient):
    headers = {"accept-language": "ru,en;q=0.9"}

    def __init__(self, agent: Agent):
        self.hdrs = json.dumps({**self.headers, **agent.auth}, separators=(",", ":"))
        super().__init__(agent)

    async def get_orders(
        self, stauts: OrderStatus = OrderStatus.created, coin: Coin = None, cur: Cur = None, is_sell: bool = None
    ) -> list[Order]:
        pass

    async def order_request(self, ad_id: int, amount: float) -> Order:
        pass

    async def my_fiats(self, cur: Cur = None) -> list[dict]:
        p = subprocess.Popen(
            ["node", "req.mjs", "user/queryPaymethods", '{"languageType":6}', self.hdrs], stdout=subprocess.PIPE
        )
        out = p.stdout.read().decode()
        fiats: list[dict] = json.loads(out)
        return [
            {
                "id": f["userPaymethodId"],
                "pmex.exid": f["paymethodId"],
                **{d["type"] + ("" if d["required"] else "_"): d["value"] for d in f["paymethodInfo"]},
            }
            for f in fiats
        ]

    async def fiat_new(self, fiat: FiatNew) -> Fiat.pyd():
        pass

    async def fiat_upd(self, detail: str = None, typ: PmType = None) -> bool:
        pass

    async def fiat_del(self, fiat_id: int) -> bool:
        pass

    async def my_ads(self) -> list[Ad]:
        pass

    async def ad_new(
        self,
        coin: Coin,
        cur: Cur,
        is_sell: bool,
        pms: list[Pm],
        price: float,
        is_float: bool = True,
        min_fiat: int = None,
        details: str = None,
        autoreply: str = None,
        status: AdStatus = AdStatus.active,
    ) -> Ad:
        pass

    async def ad_upd(
        self,
        pms: [Pm] = None,
        price: float = None,
        is_float: bool = None,
        min_fiat: int = None,
        details: str = None,
        autoreply: str = None,
        status: AdStatus = None,
    ) -> bool:
        pass

    async def ad_del(self) -> bool:
        pass

    async def ad_switch(self) -> bool:
        pass

    async def ads_switch(self) -> bool:
        pass

    async def get_user(self, user_id) -> User:
        pass

    async def send_user_msg(self, msg: str, file=None) -> bool:
        pass

    async def block_user(self, is_blocked: bool = True) -> bool:
        pass

    async def rate_user(self, positive: bool) -> bool:
        pass


async def main():
    from xync_schema import TORM

    _ = await init_db(TORM, True)
    agent = await Agent.get(ex__name="BitGet").prefetch_related("ex")
    cl = Client(agent)
    await cl.my_fiats()
    await cl.close()


run(main())
