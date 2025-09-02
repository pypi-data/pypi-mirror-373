import json
import logging
import re
from datetime import datetime, timezone
from uuid import uuid4

import websockets
from asyncio import run
from decimal import Decimal

from playwright.async_api import async_playwright
from pyro_client.client.file import FileClient
from tortoise.transactions import in_transaction
from xync_schema.models import CredEx

from xync_client.Abc.PmAgent import PmAgentClient
from xync_schema import models
from xync_schema.enums import UserStatus, OrderStatus

from xync_client.Pms.Payeer import Client
from xync_client.Bybit.etype.order import (
    StatusChange,
    CountDown,
    SellerCancelChange,
    Read,
    Receive,
    OrderFull,
    StatusApi,
)
from xync_client.loader import TOKEN
from xync_client.Abc.InAgent import BaseInAgentClient
from xync_client.Bybit.agent import AgentClient


class InAgentClient(BaseInAgentClient):
    agent_client: AgentClient

    async def start_listen(self):
        t = await self.agent_client.ott()
        ts = int(float(t["time_now"]) * 1000)
        await self.ws_prv(self.agent_client.actor.agent.auth["deviceId"], t["result"], ts)

    # 3N: [T] - Уведомление об одобрении запроса на сделку
    async def request_accepted_notify(self) -> int: ...  # id

    async def ws_prv(self, did: str, tok: str, ts: int):
        u = f"wss://ws2.bybit.com/private?appid=bybit&os=web&deviceid={did}&timestamp={ts}"
        async with websockets.connect(u) as websocket:
            auth_msg = json.dumps({"req_id": did, "op": "login", "args": [tok]})
            await websocket.send(auth_msg)

            sub_msg = json.dumps({"op": "subscribe", "args": ["FIAT_OTC_TOPIC", "FIAT_OTC_ONLINE_TOPIC"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"SUPER_DEAL"}']})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"OTC_ORDER_STATUS"}']})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"WEB_THREE_SELL"}']})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"APPEALED_CHANGE"}']})
            await websocket.send(sub_msg)

            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.cashier.order"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.cashier.order-eftd-complete-privilege-event"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.cashier.order-savings-product-event"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.deal-core.order-savings-complete-event"]})
            await websocket.send(sub_msg)

            sub_msg = json.dumps({"op": "subscribe", "args": ["FIAT_OTC_TOPIC", "FIAT_OTC_ONLINE_TOPIC"]})
            await websocket.send(sub_msg)
            while resp := await websocket.recv():
                if data := json.loads(resp):
                    upd, order_db = None, None
                    logging.info(f" {datetime.now().strftime('%H:%M:%S')} upd: {data.get('topic')}:{data.get('type')}")
                    match data.get("topic"):
                        case "OTC_ORDER_STATUS":
                            match data["type"]:
                                case "STATUS_CHANGE":
                                    upd = StatusChange.model_validate(data["data"])
                                    order = self.agent_client.api.get_order_details(orderId=upd.id)
                                    order = OrderFull.model_validate(order["result"])
                                    order_db = await models.Order.get_or_none(
                                        exid=order.id, ad__exid=order.itemId
                                    ) or await self.agent_client.create_order(order)
                                    match upd.status:
                                        case StatusApi.created:
                                            logging.info(f"Order {order.id} created at {order.createDate}")
                                            if upd.side == 1:  # я покупатель - ждем мою оплату
                                                dest = order.paymentTermList[0].accountNo
                                                if not re.match(r"^P\d{8,10}$", dest):
                                                    continue
                                                await order_db.fetch_related("ad__pair_side__pair", "cred__pmcur__cur")
                                                await self.send_payment(order_db, dest)
                                        case StatusApi.wait_for_buyer:
                                            if upd.side == 0:  # ждем когда покупатель оплатит
                                                if not (pmacdx := await self.get_pma_by_cdex(order)):
                                                    continue
                                                pma, cdx = pmacdx
                                                am, tid = pma.check_in(
                                                    Decimal(order.amount),
                                                    cdx.cred.pmcur.cur.ticker,
                                                    datetime.fromtimestamp(float(order.createDate) / 1000),
                                                )
                                                if not tid:
                                                    logging.info(
                                                        f"Order {order.id} created at {order.createDate}, not paid yet"
                                                    )
                                                    continue
                                                t, is_new = await models.Transfer.update_or_create(
                                                    dict(
                                                        amount=int(float(order.amount)) * 100,
                                                        accepted_at=datetime.now(timezone.utc),
                                                    ),
                                                    order=order_db,
                                                    pmid=tid,
                                                )
                                                if not is_new:
                                                    continue
                                                await order_db.fetch_related("ad__pair_side__pair")
                                                async with in_transaction():
                                                    # добавляем остаток монеты
                                                    ass = await models.Asset.get(
                                                        addr__coin_id=order_db.ad.pair_side.pair.coin_id,
                                                        addr__actor=self.agent_client.actor,
                                                    )
                                                    ass.free -= float(order_db.amount / order_db.ad.price)
                                                    await ass.save(update_fields=["free"])
                                                    # обновляем остаток валюты
                                                    fiat = await models.Fiat.get(cred_id=order_db.cred_id)
                                                    fiat.amount += order_db.amount
                                                    await fiat.save(update_fields=["amount"])
                                                    # отправляем деньги
                                                    self.agent_client.api.release_assets(orderId=upd.id)
                                                    logging.info(
                                                        f"Order {order.id} created, paid before #{tid}:{am} at {order.createDate}, and RELEASED at {datetime.now()}"
                                                    )
                                            elif upd.side == 1:  # я покупатель - ждем мою оплату
                                                continue  # logging.warning(f"Order {order.id} PAID at {datetime.now()}: {int_am}")
                                            else:
                                                ...
                                            # todo: check is always canceling
                                            # await order_db.update_from_dict({"status": OrderStatus.canceled}).save()
                                            # logging.info(f"Order {order.id} canceled at {datetime.now()}")
                                        case StatusApi.appealed:
                                            # todo: appealed by WHO? щас наугад стоит by_seller
                                            await order_db.update_from_dict(
                                                {
                                                    "status": OrderStatus.appealed_by_seller,
                                                    "appealed_at": datetime.fromtimestamp(
                                                        float(order.updateDate) / 1000
                                                    ),
                                                }
                                            ).save()
                                            logging.info(f"Order {order.id} appealed at {order_db.appealed_at}")
                                        case StatusApi.canceled:
                                            await order_db.update_from_dict({"status": OrderStatus.canceled}).save()
                                            logging.info(f"Order {order.id} canceled at {datetime.now()}")
                                        case StatusApi.completed:
                                            await order_db.update_from_dict(
                                                {
                                                    "status": OrderStatus.completed,
                                                    "confirmed_at": datetime.fromtimestamp(
                                                        float(order.updateDate) / 1000
                                                    ),
                                                }
                                            ).save()
                                            logging.info(f"Order {order.id} completed at {order_db.confirmed_at}")
                                        case StatusApi.wait_for_seller:
                                            if order_db.status == OrderStatus.paid:
                                                continue
                                            await order_db.update_from_dict(
                                                {
                                                    "status": OrderStatus.paid,
                                                    "payed_at": datetime.fromtimestamp(
                                                        float(order.transferDate) / 1000
                                                    ),
                                                }
                                            ).save()
                                            logging.info(f"Order {order.id} payed at {order_db.payed_at}")
                                        case _:
                                            logging.warning(f"Order {order.id} UNKNOWN STATUS {datetime.now()}")
                                case "COUNT_DOWN":
                                    upd = CountDown.model_validate(data["data"])
                                case _:
                                    self.listen(data)
                        case "OTC_USER_CHAT_MSG":
                            match data["type"]:
                                case "RECEIVE":
                                    upd = Receive.model_validate(data["data"])
                                    if order_db := await models.Order.get_or_none(
                                        exid=upd.orderId, ad__maker__ex=self.agent_client.actor.ex
                                    ).prefetch_related("ad__pair_side__pair", "cred__pmcur__cur"):
                                        im_taker = order_db.taker_id == self.agent_client.actor.id
                                        im_buyer = order_db.ad.pair_side.is_sell == im_taker
                                        if order_db.ad.auto_msg != upd.message and upd.roleType not in ("sys", "alarm"):
                                            msg, _ = await models.Msg.update_or_create(
                                                {
                                                    "to_maker": upd.userId == self.agent_client.actor.exid and im_taker,
                                                },
                                                sent_at=datetime.fromtimestamp(float(upd.createDate) / 1000),
                                                txt=upd.message,
                                                order=order_db,
                                            )
                                            if not upd.message:
                                                ...
                                            if im_buyer and re.match(r"^P\d{8,10}$", upd.message):
                                                await self.send_payment(order_db, upd.message)
                                case "READ":
                                    upd = Read.model_validate(data["data"])
                                    # if upd.status not in (StatusWs.created, StatusWs.canceled, 10, StatusWs.completed):
                                    if upd.orderStatus in (
                                        StatusApi.wait_for_buyer,
                                    ):  # todo: тут приходит ордер.статус=10, хотя покупатель еще не нажал оплачено
                                        order = self.agent_client.api.get_order_details(orderId=upd.orderId)["result"]
                                        order = OrderFull.model_validate(order)

                                case "CLEAR":
                                    continue
                                case _:
                                    self.listen(data)
                        case "OTC_USER_CHAT_MSG_V2":
                            # match data["type"]:
                            #     case "RECEIVE":
                            #         upd = Receive.model_validate(data["data"])
                            #     case "READ":
                            #         upd = Read.model_validate(data["data"])
                            #     case "CLEAR":
                            #         pass
                            #     case _:
                            #         self.listen(data)
                            continue
                        case "SELLER_CANCEL_CHANGE":
                            upd = SellerCancelChange.model_validate(data["data"])
                        case None:
                            if not data.get("success"):
                                logging.error(data, "NOT SUCCESS!")
                            else:
                                continue  # success login, subscribes, input
                        case _:
                            logging.warning(data, "UNKNOWN TOPIC")
                    if not upd:
                        logging.warning(data, "NOT PROCESSED UPDATE")

    async def send_payment(self, order_db: models.Order, dest):
        if order_db.status not in (OrderStatus.created, OrderStatus.requested):
            return
        int_am = int(float(order_db.amount))
        pma, cur = await self.get_pma_by_pmex(order_db)
        async with in_transaction():
            # отмечаем ордер на бирже "оплачен"
            pmex = await models.PmEx.get(pm_id=order_db.cred.pmcur.pm_id, ex=self.agent_client.actor.ex)
            credex = await models.CredEx.get(cred=order_db.cred, ex=self.agent_client.actor.ex)
            self.agent_client.api.mark_as_paid(
                orderId=str(order_db.exid),
                paymentType=pmex.exid,  # pmex.exid
                paymentId=str(credex.exid),  # credex.exid
            )
            # проверяем не отправляли ли мы уже перевод по этому ордеру
            if t := await models.Transfer.get_or_none(order=order_db, amount=int_am):
                await pma.bot.send(f"Order# {order_db.exid}: Double send {int_am}{cur} to {dest} #{t.pmid}!")
                raise Exception(f"Order# {order_db.exid}: Double send {int_am}{cur} to {dest} #{t.pmid}!")

            # ставим в бд статус "оплачен"
            order_db.status = OrderStatus.paid
            order_db.payed_at = datetime.now(timezone.utc)
            await order_db.save()
            # добавляем остаток монеты
            ass = await models.Asset.get(
                addr__coin_id=order_db.ad.pair_side.pair.coin_id, addr__actor=self.agent_client.actor
            )
            ass.free += float(order_db.amount / order_db.ad.price)
            await ass.save(update_fields=["free"])
            # отправляем деньги
            tid, img, rest_amount = await pma.send(dest=dest, amount=int_am, cur=cur)
            # создаем перевод в бд
            t, _ = await models.Transfer.update_or_create(
                {"amount": int_am * 100},
                order=order_db,
                pmid=tid,
            )
            # обновляем остаток валюты
            await models.Fiat.update_or_create({"amount": rest_amount}, cred_id=order_db.cred_id)
            # отправляем продавцу чек
            if res := self.agent_client.api.upload_chat_file(upload_file=f"tmp/{dest}.png").get("result"):
                self.agent_client.api.send_chat_message(
                    orderId=str(order_db.exid), contentType="pic", message=res["url"], msgUuid=uuid4().hex
                )
            logging.info(f"Order {order_db.exid} PAID at {datetime.now()}: {int_am}!")

    async def get_pma_by_cdex(self, order: OrderFull) -> tuple[PmAgentClient | None, CredEx] | None:
        cdxs = await models.CredEx.filter(
            ex=self.agent_client.ex_client.ex,
            exid__in=[ptl.id for ptl in order.paymentTermList],
            cred__person=self.agent_client.actor.person,
        ).prefetch_related("cred__pmcur__cur")
        pmas = [pma for cdx in cdxs if (pma := self.pmacs.get(cdx.cred.pmcur.pm_id))]
        if not len(pmas):
            raise Exception(order.paymentTermList, f"No pm_agents for {order.paymentTermList[0].paymentType}")
        elif len(pmas) > 1:
            logging.error(order.paymentTermList, f">1 pm_agents for {cdxs[0].cred.pmcur.pm_id}")
        else:
            return pmas[0], cdxs[0]

    async def get_pma_by_pmex(self, order_db: models.Order) -> tuple[PmAgentClient, str]:
        pma = self.pmacs.get(order_db.cred.pmcur.pm_id)
        if pma:
            return pma, order_db.cred.pmcur.cur.ticker
        logging.error(f"No pm_agents for {order_db.cred.pmcur.pm_id}")

    @staticmethod
    def listen(data: dict | None):
        # print(data)
        ...


async def main():
    from x_model import init_db
    from xync_client.loader import TORM

    _ = await init_db(TORM, True)
    logging.basicConfig(level=logging.INFO)

    actor = (
        await models.Actor.filter(
            ex_id=9,
            agent__auth__isnull=False,
            person__user__status=UserStatus.ACTIVE,
            person__user__pm_agents__isnull=False,
        )
        .prefetch_related("ex", "agent", "person__user__pm_agents")
        .first()
    )

    async with FileClient(TOKEN) as b:
        cl: InAgentClient = actor.in_client(b)
        # await cl.agent_client.export_my_ads()
        payeer_cl = Client(actor.person.user.username_id)
        for pma in actor.person.user.pm_agents:
            cl.pmacs[pma.pm_id] = await payeer_cl.start(await async_playwright().start(), True)

        _ = await cl.start_listen()
        await cl.agent_client.close()


if __name__ == "__main__":
    run(main())
