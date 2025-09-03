from json import dumps

from x_client.aiohttp import Client
from xync_schema.enums import AdStatus, PmType, OrderStatus
from xync_schema.models import Pm, Coin, Cur, Ad, Order
from xync_schema import models
from xync_client.Abc.Agent import BaseAgentClient
from xync_client.Htx.etype import test

import logging

url_ads_req = "https://otc-cf.huobi.com/v1/data/trade-market"
url_ads_web = "https://www.huobi.com/en-us/fiat-crypto/trade/"
url_my_ads = "https://otc-api.trygofast.com/v1/data/trade-list?pageSize=50"
url_my_ad = "https://www.huobi.com/-/x/otc/v1/otc/trade/"  # + id
url_my_bals = "https://www.huobi.com/-/x/otc/v1/capital/balance"
url_paccs = "https://www.huobi.com/-/x/otc/v1/user/receipt-account"


class Public(Client):
    url_ads_web = "https://www.huobi.com/en-us/fiat-crypto/trade/"


class AgentClient(BaseAgentClient):
    headers = {
        "portal": "web",
    }

    async def creds(self) -> list[test.CredEpyd]:
        resp = await self._get("/-/x/otc/v1/user/receipt-account")
        return [test.CredEpyd(**cred) for cred in resp["data"]]

    async def cred_del(self, cred_id: int) -> int:
        data = {"id": str(cred_id), "password": self.actor.agent.auth["password"]}

        cred_del = await self._post("/-/x/otc/v1/user/receipt-account/remove", data=data)
        if cred_del["message"] == "Success":
            await (await models.CredEx.get(exid=cred_id)).delete()
            return cred_id
        else:
            logging.error(cred_del)

    async def dynamicModelInfo(self, pids: str):
        resp = await self._get("/-/x/otc/v1/user/receipt-account/dynamicModelInfo", {"payMethodIds": pids})
        return resp["data"]["modelFields"]

    async def cred_new(self, cred: models.Cred) -> models.CredEx:
        pmcur = await cred.pmcur
        exid = str(await models.PmEx.get(pm_id=pmcur.pm_id, ex=self.ex_client.ex).values_list("exid", flat=True))
        field_map = {
            "payee": "name",
            "bank": "extra",
            "sub_bank": "extra",
            "pay_account": "detail",
        }
        fields = {f["fieldType"]: f["fieldId"] for f in await self.dynamicModelInfo(exid)}
        # Данные, где modelFields теперь список ModelField
        data = {
            "payMethod": exid,
            "password": self.actor.agent.auth["password"],
            "modelFields": dumps(
                [{"fieldId": fid, "fieldType": ft, "value": getattr(cred, field_map[ft])} for ft, fid in fields.items()]
            ),
        }
        resp = await self._post("/-/x/otc/v1/user/receipt-account/addByDynamicModel", data=data)
        if not resp["success"]:
            logging.exception(resp["message"])
        res = test.Result(**resp)
        credex, _ = await models.CredEx.update_or_create({"cred": cred, "ex": self.ex}, exid=res.data.id)
        return credex

    async def cred_upd(self, cred: models.Cred, exid: int) -> models.CredEx:
        pmcur = await cred.pmcur
        _exid = str(await models.PmEx.get(pm_id=pmcur.pm_id, ex=self.ex_client.ex).values_list("exid", flat=True))
        field_map = {
            "payee": "name",
            "bank": "extra",
            "sub_bank": "extra",
            "pay_account": "detail",
        }
        fields = {f["fieldType"]: f["fieldId"] for f in await self.dynamicModelInfo(_exid)}
        # Данные, где modelFields теперь список ModelField
        data = {
            "payMethod": exid,
            "password": self.actor.agent.auth["headers"]["password"],
            "modelFields": dumps(
                [{"fieldId": fid, "fieldType": ft, "value": getattr(cred, field_map[ft])} for ft, fid in fields.items()]
            ),
            "id": exid,
        }
        await self._post("/-/x/otc/v1/user/receipt-account/modifyByDynamicModel", data=data)
        cred_ids = await models.Cred.filter(credexs__exid=exid).values_list("id", flat=True)
        await models.Cred.filter(id__in=cred_ids).update(name=cred.name, detail=cred.detail)
        return await models.CredEx.filter(exid=exid).first()

    # 0
    async def get_orders(
        self, stauts: OrderStatus = OrderStatus.created, coin: Coin = None, cur: Cur = None, is_sell: bool = None
    ) -> list[Order]:
        pass

    async def order_request(self, ad_id: int, amount: float) -> dict:
        pass

    async def my_fiats(self, cur: Cur = None) -> list[dict]:
        pass

    # async def fiat_new(self, fiat: FiatNew) -> Fiat.pyd():
    #     pass

    async def fiat_upd(self, detail: str = None, typ: PmType = None) -> bool:
        pass

    async def fiat_del(self, fiat_id: int) -> bool:
        pass

    async def my_ads(self) -> list[dict]:
        res = await self._get(url_my_ads)
        ads: [] = res["data"]
        if (pages := res["totalPage"]) > 1:
            for p in range(2, pages + 1):
                ads += (await self._get(url_my_ads, {"currPage": p})).get("data", False)
        return ads

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

    async def get_user(self, user_id: int) -> dict:
        user = (await self._get(f"/-/x/otc/v1/user/{user_id}/info"))["data"]
        return user

    async def send_user_msg(self, msg: str, file=None) -> bool:
        pass

    async def block_user(self, is_blocked: bool = True) -> bool:
        pass

    async def rate_user(self, positive: bool) -> bool:
        pass

    # 39
    async def my_assets(self) -> dict:
        assets = await self._get(url_my_bals)
        return {c["coinId"]: c["total"] for c in assets["data"] if c["total"]}

    async def _get_auth_hdrs(self) -> dict[str, str]:
        pass

    base_url = ""
    middle_url = ""

    htok: str = "Ev5lFfAvxDU2MA9BJ-Mc4U6zZG3Wb6qsp3Tx2fz6GIoY-uOP2m0-gvjE57ad1qDF"

    url_ads_req = "https://otc-cf.huobi.com/v1/data/trade-market"
    url_my_ads = "https://otc-api.trygofast.com/v1/data/trade-list?pageSize=50"
    url_my_ad = "https://www.huobi.com/-/x/otc/v1/otc/trade/"  # + id
    url_my_bals = "https://www.huobi.com/-/x/otc/v1/capital/balance"
    url_paccs = "https://www.huobi.com/-/x/otc/v1/user/receipt-account"


async def _test():
    from x_model import init_db
    from xync_schema import TORM

    _ = await init_db(TORM, True)
    actor = (
        await models.Actor.filter(ex_id=15, agent__isnull=False).prefetch_related("ex", "agent", "person__user").first()
    )
    cl: AgentClient = actor.client()
    cred = await models.Cred[89]
    _ = await cl.cred_new(cred)
    _creds = await cl.creds()
    # _ = await cl.cred_del(16984748)
    await cl.close()


if __name__ == "__main__":
    from asyncio import run

    run(_test())
