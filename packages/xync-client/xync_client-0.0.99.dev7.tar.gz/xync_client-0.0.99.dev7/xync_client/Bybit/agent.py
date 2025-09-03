import asyncio
import logging
import re
from asyncio import sleep, gather
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from difflib import SequenceMatcher
from enum import IntEnum
from http.client import HTTPException
from typing import Literal

import pyotp
from asyncpg import ConnectionDoesNotExistError
from bybit_p2p import P2P
from bybit_p2p._exceptions import FailedRequestError
from pyro_client.client.file import FileClient
from tortoise import BaseDBAsyncClient
from tortoise.exceptions import IntegrityError
from tortoise.expressions import F, Q
from tortoise.functions import Count
from tortoise.signals import post_save
from urllib3.exceptions import ReadTimeoutError
from x_model import init_db
from x_model.func import ArrayAgg
from xync_schema import models
from xync_schema.enums import OrderStatus

from xync_schema.models import Actor, Cond, CondSim, PmCur, PairSide

from xync_client.Abc.Agent import BaseAgentClient
from xync_client.Abc.xtype import BaseOrderReq, FlatDict
from xync_client.Bybit.etype.ad import AdPostRequest, AdUpdateRequest, Ad, AdStatus
from xync_client.Bybit.etype.cred import CredEpyd
from xync_client.Bybit.etype.order import (
    OrderRequest,
    PreOrderResp,
    OrderResp,
    CancelOrderReq,
    OrderItem,
    OrderFull,
    Message,
    Status,
)
from xync_client.loader import TORM, TOKEN


class NoMakerException(Exception):
    pass


class AgentClient(BaseAgentClient):  # Bybit client
    host = "api2.bybit.com"
    headers = {"cookie": ";"}  # rewrite token for public methods
    api: P2P
    last_ad_id: list[str] = []
    update_ad_body = {
        "priceType": "1",
        "premium": "118",
        "quantity": "0.01",
        "minAmount": "500",
        "maxAmount": "3500000",
        "paymentPeriod": "30",
        "remark": "",
        "price": "398244.84",
        "paymentIds": ["3162931"],
        "tradingPreferenceSet": {
            "isKyc": "1",
            "hasCompleteRateDay30": "0",
            "completeRateDay30": "",
            "hasOrderFinishNumberDay30": "0",
            "orderFinishNumberDay30": "0",
            "isMobile": "0",
            "isEmail": "0",
            "hasUnPostAd": "0",
            "hasRegisterTime": "0",
            "registerTimeThreshold": "0",
            "hasNationalLimit": "0",
            "nationalLimit": "",
        },
        "actionType": "MODIFY",
        "securityRiskToken": "",
    }
    all_conds: dict[int, tuple[str, set[int]]] = {}
    cond_sims: dict[int, int] = defaultdict(set)
    rcond_sims: dict[int, set[int]] = defaultdict(set)  # backward
    tree: dict = {}

    def __init__(self, actor: Actor, bot: FileClient, **kwargs):
        super().__init__(actor, bot, **kwargs)
        self.api = P2P(testnet=False, api_key=actor.agent.auth["key"], api_secret=actor.agent.auth["sec"])

    """ Private METHs"""

    async def fiat_new(self, payment_type: int, real_name: str, account_number: str) -> FlatDict | None:
        method1 = await self._post(
            "/fiat/otc/user/payment/new_create",
            {"paymentType": payment_type, "realName": real_name, "accountNo": account_number, "securityRiskToken": ""},
        )
        if srt := method1["result"]["securityRiskToken"]:
            await self._check_2fa(srt)
            method2 = await self._post(
                "/fiat/otc/user/payment/new_create",
                {
                    "paymentType": payment_type,
                    "realName": real_name,
                    "accountNo": account_number,
                    "securityRiskToken": srt,
                },
            )
            return method2
        else:
            return logging.exception(method1)

    async def get_payment_method(self, fiat_id: int = None) -> dict:
        list_methods = self.creds()
        if fiat_id:
            fiat = [m for m in list_methods if m["id"] == fiat_id][0]
            return fiat
        return list_methods[1]

    def creds(self) -> dict[int, CredEpyd]:
        data = self.api.get_user_payment_types()
        if data["ret_code"] > 0:
            return data
        return {credex["id"]: CredEpyd.model_validate(credex) for credex in data["result"]}

    async def cred_epyd2db(self, ecdx: CredEpyd, pers_id: int = None, cur_id: int = None) -> models.CredEx | None:
        if ecdx.paymentType in (416,):  # what is 416??
            return None
        if not (
            pmex := await models.PmEx.get_or_none(exid=ecdx.paymentType, ex=self.ex_client.ex).prefetch_related(
                "pm__curs"
            )
        ):
            raise HTTPException(f"No PmEx {ecdx.paymentType} on ex#{self.ex_client.ex.name}", 404)
        if cred_old := await models.Cred.get_or_none(credexs__exid=ecdx.id, credexs__ex=self.actor.ex).prefetch_related(
            "pmcur"
        ):
            cur_id = cred_old.pmcur.cur_id
        elif not cur_id:  # is new Cred
            cur_id = (
                pmex.pm.df_cur_id
                or (pmex.pm.country_id and (await pmex.pm.country).cur_id)
                # or (ecdx.currencyBalance and await models.Cur.get_or_none(ticker=ecdx.currencyBalance[0]))
                or (0 < len(pmex.pm.curs) < 30 and pmex.pm.curs[-1].id)
                or await self.guess_cur(ecdx)
            )
        if not cur_id:
            raise Exception(f"Set default cur for {pmex.name}")
        if not (pmcur := await models.PmCur.get_or_none(cur_id=cur_id, pm_id=pmex.pm_id)):
            raise HTTPException(f"No PmCur with cur#{ecdx.currencyBalance} and pm#{ecdx.paymentType}", 404)
        dct = {
            "pmcur_id": pmcur.id,
            "name": ecdx.realName,
            "person_id": pers_id or self.actor.person_id,
            "detail": ecdx.accountNo,
            "extra": ecdx.branchName or ecdx.bankName or ecdx.qrcode or ecdx.payMessage or ecdx.paymentExt1,
        }  # todo: WTD with multicur pms?
        cred_in = models.Cred.validate(dct, False)
        cred_db, _ = await models.Cred.update_or_create(**cred_in.df_unq())
        credex_in = models.CredEx.validate({"exid": ecdx.id, "cred_id": cred_db.id, "ex_id": self.actor.ex.id})
        credex_db, _ = await models.CredEx.update_or_create(**credex_in.df_unq())
        return credex_db

    async def guess_cur(self, ecdx: CredEpyd):
        mbs = ecdx.bankName.split(", ")
        mbs += ecdx.branchName.split(" / ")
        mbs = {mb.lower(): mb for mb in mbs}
        if (
            pms := await models.Pm.filter(Q(join_type="OR", pmexs__name__in=mbs.values(), norm__in=mbs.keys()))
            .group_by("pmcurs__cur_id", "pmcurs__cur__ticker")
            .annotate(ccnt=Count("id"), names=ArrayAgg("norm"))
            .order_by("-ccnt", "pmcurs__cur__ticker")
            .values("pmcurs__cur_id", "names", "ccnt")
        ):
            return pms[0]["pmcurs__cur_id"]
        curs = {c.ticker: c.id for c in await models.Cur.all()}
        for cur, cid in curs.items():
            if re.search(re.compile(rf"\({cur}\)$"), ecdx.bankName):
                return cid
            if re.search(re.compile(rf"\({cur}\)$"), ecdx.branchName):
                return cid
            if re.search(re.compile(rf"\({cur}\)$"), ecdx.accountNo):
                return cid
            if re.search(re.compile(rf"\({cur}\)$"), ecdx.payMessage):
                return cid
        return None

    # 25: Список реквизитов моих платежных методов
    async def set_creds(self) -> list[models.CredEx]:
        credexs_epyd: dict[int, CredEpyd] = self.creds()
        credexs: list[models.CredEx] = [await self.cred_epyd2db(f) for f in credexs_epyd.values()]
        return credexs

    async def ott(self):
        t = await self._post("/user/private/ott")
        return t

    # 27
    async def fiat_upd(self, fiat_id: int, detail: str, name: str = None) -> dict:
        fiat = self.get_payment_method(fiat_id)
        fiat["realName"] = name
        fiat["accountNo"] = detail
        result = await self._post("/fiat/otc/user/payment/new_update", fiat)
        srt = result["result"]["securityRiskToken"]
        await self._check_2fa(srt)
        fiat["securityRiskToken"] = srt
        result2 = await self._post("/fiat/otc/user/payment/new_update", fiat)
        return result2

    # 28
    async def fiat_del(self, fiat_id: int) -> dict | str:
        data = {"id": fiat_id, "securityRiskToken": ""}
        method = await self._post("/fiat/otc/user/payment/new_delete", data)
        srt = method["result"]["securityRiskToken"]
        await self._check_2fa(srt)
        data["securityRiskToken"] = srt
        delete = await self._post("/fiat/otc/user/payment/new_delete", data)
        return delete

    async def switch_ads(self, new_status: AdStatus) -> dict:
        data = {"workStatus": new_status.name}  # todo: переделать на апи, там status 0 -> 1
        res = await self._post("/fiat/otc/maker/work-config/switch", data)
        return res

    async def ads(
        self,
        cnx: models.CoinEx,
        crx: models.CurEx,
        is_sell: bool,
        pmxs: list[models.PmEx],
        amount: int = None,
        lim: int = 50,
        vm_filter: bool = False,
    ) -> list[Ad]:
        return await self.ex_client.ads(
            cnx.exid, crx.exid, is_sell, [pmex.exid for pmex in pmxs or []], amount, lim, vm_filter
        )

    def online_ads(self) -> str:
        online = self._get("/fiat/otc/maker/work-config/get")
        return online["result"]["workStatus"]

    @staticmethod
    def get_rate(list_ads: list) -> float:
        ads = [ad for ad in list_ads if set(ad["payments"]) - {"5", "51"}]
        return float(ads[0]["price"])

    def my_ads(self, active: bool = True, page: int = 1) -> list[Ad]:
        resp = self.api.get_ads_list(size="30", page=str(page), status=AdStatus.active if active else AdStatus.sold_out)
        ads = [Ad.model_validate(ad) for ad in resp["result"]["items"]]
        if resp["result"]["count"] > 30 * page:
            ads.extend(self.my_ads(active, page + 1))
        return ads

    async def export_my_ads(self, active: bool = None) -> int:  # upserted)
        ads = self.my_ads(True)
        if not active:
            ads += self.my_ads(False)
        res = [await self.ad_create(ad, actor=self.actor) for ad in ads]
        res = [await models.MyAd.update_or_create(ad=ad) for ad in res]
        return len(res)

    def get_security_token_create(self):
        data = self._post("/fiat/otc/item/create", self.create_ad_body)
        if data["ret_code"] == 912120019:  # Current user can not to create add as maker
            raise NoMakerException(data)
        security_risk_token = data["result"]["securityRiskToken"]
        return security_risk_token

    def _check_2fa(self, risk_token):
        # 2fa code
        bybit_secret = self.agent.auth["2fa"]
        totp = pyotp.TOTP(bybit_secret)
        totp_code = totp.now()

        res = self._post(
            "/user/public/risk/verify", {"risk_token": risk_token, "component_list": {"google2fa": totp_code}}
        )
        if res["ret_msg"] != "success":
            print("Wrong 2fa, wait 5 secs and retry..")
            sleep(5)
            self._check_2fa(risk_token)
        return res

    def _post_ad(self, risk_token: str):
        self.create_ad_body.update({"securityRiskToken": risk_token})
        data = self._post("/fiat/otc/item/create", self.create_ad_body)
        return data

    # создание объявлений
    def post_create_ad(self, token: str):
        result__check_2fa = self._check_2fa(token)
        assert result__check_2fa["ret_msg"] == "success", "2FA code wrong"

        result_add_ad = self._post_ad(token)
        if result_add_ad["ret_msg"] != "SUCCESS":
            print("Wrong 2fa on Ad creating, wait 9 secs and retry..")
            sleep(9)
            return self._post_create_ad(token)
        self.last_ad_id.append(result_add_ad["result"]["itemId"])

    def ad_new(self, ad: AdPostRequest):
        data = self.api.post_new_ad(**ad.model_dump())
        return data["result"]["itemId"] if data["ret_code"] == 0 else data

    def ad_upd(self, upd: AdUpdateRequest):
        params = upd.model_dump()
        data = self.api.update_ad(**params)
        return data["result"] if data["ret_code"] == 0 else data

    def get_security_token_update(self) -> str:
        self.update_ad_body["id"] = self.last_ad_id
        data = self._post("/fiat/otc/item/update", self.update_ad_body)
        security_risk_token = data["result"]["securityRiskToken"]
        return security_risk_token

    def post_update_ad(self, token):
        result__check_2fa = self._check_2fa(token)
        assert result__check_2fa["ret_msg"] == "success", "2FA code wrong"

        result_update_ad = self.update_ad(token)
        if result_update_ad["ret_msg"] != "SUCCESS":
            print("Wrong 2fa on Ad updating, wait 10 secs and retry..")
            sleep(10)
            return self._post_update_ad(token)
        # assert result_update_ad['ret_msg'] == 'SUCCESS', "Ad isn't updated"

    def update_ad(self, risk_token: str):
        self.update_ad_body.update({"securityRiskToken": risk_token})
        data = self._post("/fiat/otc/item/update", self.update_ad_body)
        return data

    def ad_del(self, ad_id: int):
        data = self.api.remove_ad(itemId=ad_id)
        return data

    async def order_request(self, br: BaseOrderReq) -> OrderResp:
        res0 = await self._post("/fiat/otc/item/simple", data={"item_id": str(br.ad_id)})
        if res0["ret_code"] == 0:
            res0 = res0["result"]
        res0 = PreOrderResp.model_validate(res0)
        req = OrderRequest(
            itemId=br.ad_id,
            tokenId=br.coin_exid,
            currencyId=br.cur_exid,
            side=str(OrderRequest.Side(int(br.is_sell))),
            amount=str(br.fiat_amount or br.asset_amount * float(res0.price)),
            curPrice=res0.curPrice,
            quantity=str(br.asset_amount or round(br.fiat_amount / float(res0.price), br.coin_scale)),
            flag="amount" if br.amount_is_fiat else "quantity",
        )
        # вот непосредственно сам запрос на ордер
        res = await self._post("/fiat/otc/order/create", data=req.model_dump())
        if res["ret_code"] == 0:
            return OrderResp.model_validate(res["result"])
        elif res["ret_code"] == 912120030 or res["ret_msg"] == "The price has changed, please try again later.":
            return await self.order_request(br)

    async def cancel_order(self, order_id: str) -> bool:
        cr = CancelOrderReq(orderId=order_id)
        res = await self._post("/fiat/otc/order/cancel", cr.model_dump())
        return res["ret_code"] == 0

    def get_order_info(self, order_id: str) -> dict:
        data = self._post("/fiat/otc/order/info", json={"orderId": order_id})
        return data["result"]

    def get_chat_msg(self, order_id):
        data = self._post("/fiat/otc/order/message/listpage", json={"orderId": order_id, "size": 100})
        msgs = [
            {"text": msg["message"], "type": msg["contentType"], "role": msg["roleType"], "user_id": msg["userId"]}
            for msg in data["result"]["result"]
            if msg["roleType"] not in ("sys", "alarm")
        ]
        return msgs

    def block_user(self, user_id: str):
        return self._post("/fiat/p2p/user/add_block_user", {"blockedUserId": user_id})

    def unblock_user(self, user_id: str):
        return self._post("/fiat/p2p/user/delete_block_user", {"blockedUserId": user_id})

    def user_review_post(self, order_id: str):
        return self._post(
            "/fiat/otc/order/appraise/modify",
            {
                "orderId": order_id,
                "anonymous": "0",
                "appraiseType": "1",  # тип оценки 1 - хорошо, 0 - плохо. При 0 - обязательно указывать appraiseContent
                "appraiseContent": "",
                "operateType": "ADD",  # при повторном отправлять не 'ADD' -> а 'EDIT'
            },
        )

    def get_orders_active(self, begin_time: int, end_time: int, status: int, side: int, token_id: str):
        return self._post(
            "/fiat/otc/order/pending/simplifyList",
            {
                "status": status,
                "tokenId": token_id,
                "beginTime": begin_time,
                "endTime": end_time,
                "side": side,  # 1 - продажа, 0 - покупка
                "page": 1,
                "size": 10,
            },
        )

    def get_orders_done(self, begin_time: int, end_time: int, status: int, side: int, token_id: str):
        return self._post(
            "/fiat/otc/order/simplifyList",
            {
                "status": status,  # 50 - завершено
                "tokenId": token_id,
                "beginTime": begin_time,
                "endTime": end_time,
                "side": side,  # 1 - продажа, 0 - покупка
                "page": 1,
                "size": 10,
            },
        )

    async def create_order(self, order: OrderFull) -> models.Order:
        ad = Ad(**self.api.get_ad_details(itemId=order.itemId)["result"])
        await sleep(1)
        curex = await models.CurEx.get_or_none(ex=self.ex_client.ex, exid=order.currencyId).prefetch_related("cur")
        cur_scale = (curex.scale if curex.scale is not None else curex.cur.scale) if curex else 2
        coinex = await models.CoinEx.get(ex=self.ex_client.ex, exid=order.tokenId).prefetch_related("coin")
        coin_scale = coinex.scale if coinex.scale is not None else coinex.cur.scale
        maker_name = order.buyerRealName, order.sellerRealName
        im_maker = int(order.makerUserId == order.userId)
        taker_id = (order.userId, order.targetUserId)[im_maker]
        taker_person = await self.person_upsert(maker_name[::-1][ad.side], taker_id)
        seller_person = (
            self.actor.person if order.side else await self.person_upsert(order.sellerRealName, int(order.targetUserId))
        )
        taker_nick = (self.actor.name, order.targetNickName)[im_maker]  # todo: check
        ad_db, cond_isnew = await self.cond_upsert(ad, maker_name[ad.side], force=True)
        if not ad_db:
            ...
        ecredex: CredEpyd = order.confirmedPayTerm
        if ecredex.paymentType:
            if not (credex := await models.CredEx.get_or_none(exid=ecredex.id, ex=self.ex_client.ex)):
                # cur_id = await Cur.get(ticker=ad.currencyId).values_list('id', flat=True)
                # await self.cred_epyd2db(ecredex, ad_db.maker.person_id, cur_id)
                if (
                    await PmCur.filter(
                        pm__pmexs__ex=self.ex_client.ex,
                        pm__pmexs__exid=ecredex.paymentType,
                        cur__ticker=ad.currencyId,
                    ).count()
                    != 1
                ):
                    ...
                if not (
                    pmcur := await PmCur.get_or_none(
                        pm__pmexs__ex=self.ex_client.ex,
                        pm__pmexs__exid=ecredex.paymentType,
                        cur__ticker=ad.currencyId,
                    )
                ):
                    ...
                if not (
                    crd := await models.Cred.get_or_none(pmcur=pmcur, person=seller_person, detail=ecredex.accountNo)
                ):
                    extr = ", ".join(
                        x
                        for xtr in [
                            ecredex.bankName,
                            ecredex.branchName,
                            ecredex.qrcode,
                            ecredex.payMessage,
                            ecredex.paymentExt1,
                        ]
                        if (x := xtr.strip())
                    )
                    crd = await models.Cred.create(
                        detail=ecredex.accountNo,
                        pmcur=pmcur,
                        person=seller_person,
                        name=ecredex.realName,
                        extra=extr,
                    )
                credex = await models.CredEx.create(exid=ecredex.id, ex=self.ex_client.ex, cred=crd)
        try:
            taker, _ = await Actor.get_or_create(
                {"name": taker_nick, "person": taker_person}, ex=self.ex_client.ex, exid=taker_id
            )
        except IntegrityError as e:
            logging.error(e)
        odb, _ = await models.Order.update_or_create(
            {
                "amount": float(order.amount) * 10**cur_scale,
                "quantity": float(order.quantity) * 10**coin_scale,
                "status": OrderStatus[Status(order.status).name],
                "created_at": int(order.createDate[:-3]),
                "payed_at": order.transferDate != "0" and int(order.transferDate[:-3]) or None,
                "confirmed_at": Status(order.status) == Status.completed and int(order.updateDate[:-3]) or None,
                "appealed_at": order.status == 30 and int(order.updateDate[:-3]) or None,
                "cred_id": ecredex.paymentType and credex.cred_id or None,
                "taker": taker,
                "ad": ad_db,
            },
            exid=order.id,
        )
        await odb.fetch_related("ad")
        return odb

    async def get_api_orders(
        self,
        page: int = 1,
        begin_time: int = None,
        end_time: int = None,
        status: int = None,
        side: int = None,
        token_id: str = None,
    ):
        try:
            lst = self.api.get_orders(
                page=page,
                size=30,
                # status=status,  # 50 - завершено
                # tokenId=token_id,
                # beginTime=begin_time,
                # endTime=end_time,
                # side=side,  # 1 - продажа, 0 - покупка
            )
        except FailedRequestError as e:
            if e.status_code == 10000:
                await sleep(9)
                await self.get_api_orders(page, begin_time, end_time, status, side, token_id)
        ords = {int(o["id"]): OrderItem.model_validate(o) for o in lst["result"]["items"]}
        for oid, o in ords.items():
            fo = self.api.get_order_details(orderId=o.id)
            order = OrderFull.model_validate(fo["result"])
            order_db = await self.create_order(order)
            await sleep(1)
            dmsgs = self.api.get_chat_messages(orderId=oid, size=200)["result"]["result"][::-1]
            msgs = [Message.model_validate(m) for m in dmsgs if m["msgType"] in (1, 2, 7, 8)]
            if order_db.ad.auto_msg:
                msgs.pop(0)
            msgs_db = [
                models.Msg(
                    order=order_db,
                    read=m.isRead,
                    to_maker=m.userId != order.makerUserId,
                    **({"txt": m.message} if m.msgType == 1 else {"file": await self.ex_client.file_upsert(m.message)}),
                    sent_at=int(m.createDate[:-3]),
                )
                for m in msgs
            ]
            _ = await models.Msg.bulk_create(msgs_db, ignore_conflicts=True)
        logging.info(f"orders page#{page} imported ok!")
        if len(ords) == 30:
            await self.get_api_orders(page + 1, begin_time, end_time, status, side, token_id)

    async def mad_upd(self, mad: Ad, attrs: dict, cxids: list[str]):
        if not [setattr(mad, k, v) for k, v in attrs.items() if getattr(mad, k) != v]:
            print(end="v" if mad.side else "^", flush=True)
            return await sleep(5)
        req = AdUpdateRequest.model_validate({**mad.model_dump(), "paymentIds": cxids})
        try:
            return self.ad_upd(req)
        except FailedRequestError as e:
            if ExcCode(e.status_code) == ExcCode.FixPriceLimit:
                if limits := re.search(
                    r"The fixed price set is lower than ([0-9]+\.?[0-9]{0,2}) or higher than ([0-9]+\.?[0-9]{0,2})",
                    e.message,
                ):
                    return await self.mad_upd(mad, {"price": limits.group(1 if mad.side else 2)}, cxids)
            elif ExcCode(e.status_code) == ExcCode.RareLimit:
                await sleep(180)
            else:
                raise e
        except (ReadTimeoutError, ConnectionDoesNotExistError):
            logging.warning("Connection failed. Restarting..")
        print("-" if mad.side else "+", end=req.price, flush=True)
        await sleep(60)

    def overprice_filter(self, ads: list[Ad], ceil: Decimal, k: Literal[-1, 1]):
        # вырезаем ads с ценами выше потолка
        if ads and (ceil - Decimal(ads[0].price)) * k > 0:
            if int(ads[0].userId) != self.actor.exid:
                ads.pop(0)
                self.overprice_filter(ads, ceil, k)

    def get_cad(self, ads: list[Ad], ceil: Decimal, k: Literal[-1, 1], target_place: int, cur_plc: int) -> Ad:
        if not ads:
            return None
        # чью цену будем обгонять, предыдущей или слещующей объявы?
        # cad: Ad = ads[place] if cur_plc > place else ads[cur_plc]
        # переделал пока на жесткую установку целевого места, даже если текущее выше:
        if len(ads) <= target_place:
            logging.error(f"target place {target_place} not found in ads list {ads}")
        cad: Ad = ads[target_place]
        # а цена обгоняемой объявы не выше нашего потолка?
        if (Decimal(cad.price) - ceil) * k <= 0:
            # тогда берем следующую
            ads.pop(target_place)
            cad = self.get_cad(ads, ceil, k, target_place, cur_plc)
        # todo: добавить фильтр по лимитам min-max
        return cad

    # @staticmethod
    # def premium_up(mad: Ad, cad: Ad, k: Literal[-1, 1]):
    #     mpc, mpm, cpc, cpm = Decimal(mad.price), Decimal(mad.premium), Decimal(cad.price), Decimal(cad.premium)
    #     new_premium = cpm - k * step(mad, cad, 2)
    #     if Decimal(mad.premium) == new_premium:  # Если нужный % и так уже стоит
    #         raise ValueError("wrong premium", mad, cad)
    #     if round(cpc * new_premium / cpm, 2) == m
    #     mad.premium = new_premium.to_eng_string()

    async def racing(
        self,
        race: models.Race,
    ):
        coinex: models.CoinEx = await models.CoinEx.get(
            coin_id=race.road.ad.pair_side.pair.coin_id, ex=self.actor.ex
        ).prefetch_related("coin")
        curex: models.CurEx = await models.CurEx.get(
            cur_id=race.road.ad.pair_side.pair.cur_id, ex=self.actor.ex
        ).prefetch_related("cur")
        taker_side: bool = not race.road.ad.pair_side.is_sell
        pm_ids = [pm.id for pm in race.road.ad.pms]
        pmexs: list[models.PmEx] = await models.PmEx.filter(pm_id__in=pm_ids, ex=self.actor.ex).prefetch_related("pm")
        k = (-1) ** int(taker_side)  # on_buy=1, on_sell=-1
        sleep_sec = 3  # 1 if set(pms) & {"volet"} and coinex.coin_id == 1 else 5
        creds: list[models.CredEx] = await self.get_credexs_by_pms(race.road.ad.pms, curex.cur_id)
        lstat, volume = None, 0

        while self.actor.person.user.status > 0:
            # обновляем все обновления по текущей гонке из бд
            await race.refresh_from_db()
            if not race.started:
                await sleep(5)
                continue
            # если гонка дольше Х минут не обновлялась, обновляем ее (и ее пары) потолок
            expiration = datetime.now(timezone.utc) - timedelta(minutes=15)
            if race.updated_at < expiration:
                ceils, hp, vmf, zplace = await self.get_ceils(coinex, curex, pmexs, 0.001, True)
                race.ceil = ceils[int(taker_side)]
                await race.save()
                # upd pair race
                if prace := await models.Race.annotate(pms_count=Count("road__ad__pms")).get_or_none(
                    road__ad__pair_side__pair_id=race.road.ad.pair_side.pair_id,
                    road__ad__pair_side__is_sell=taker_side,
                    road__ad__maker=self.actor,
                    updated_at__lt=expiration,
                    road__ad__pms__id__in=pm_ids,
                    pms_count=len(pm_ids),
                ):
                    prace.ceil = ceils[int(not taker_side)]
                    await prace.save()

            last_vol = volume
            if taker_side:  # гонка в стакане продажи - мы покупаем монету за ФИАТ
                fiat = max(await models.Fiat.filter(cred_id__in=[c.cred_id for c in creds]), key=lambda x: x.amount)
                volume = fiat.amount / race.road.ad.price
            else:  # гонка в стакане покупки - мы продаем МОНЕТУ за фиат
                asset = await models.Asset.get(addr__actor=self.actor, addr__coin_id=coinex.coin_id)
                volume = asset.free - (asset.freeze or 0) - (asset.lock or 0)
            volume = str(round(volume, coinex.scale))

            ads: list[Ad] = await self.ads(coinex, curex, taker_side, pmexs)
            if race.vm_filter:
                ads = [ad for ad in ads if "VA" in ad.authTag]
            self.overprice_filter(ads, race.ceil, k)  # обрезаем сверху все ads дороже нашего потолка

            if 571 in pm_ids and coinex.coin.ticker == "USDT" and not taker_side:
                ...

            if not ads:
                print(coinex.exid, curex.exid, taker_side, "no ads!")
                await sleep(15)
                continue
            # определяем наше текущее место в уже обрезанном списке ads
            if not (cur_plc := [i for i, ad in enumerate(ads) if int(ad.userId) == self.actor.exid]):
                logging.warning(f"No racing in {pmexs[0].name} {'-' if taker_side else '+'}{coinex.exid}/{curex.exid}")
                await sleep(15)
                continue
            (cur_plc,) = cur_plc  # может упасть если в списке > 1 наш ad
            rads = [(await self.cond_upsert(ad, ps=race.road.ad.pair_side, force=True))[0] for ad in ads[:cur_plc]]
            rivals = [
                (await models.Rival.update_or_create({"place": plc, "price": ad.price, "premium": ad.premium}, ad=ad))[
                    0
                ]
                for plc, ad in enumerate(rads)
            ]
            mad: Ad = ads.pop(cur_plc)
            if (
                not (lstat := lstat or await race.stats.order_by("-created_at").first())
                or lstat.place != cur_plc
                or lstat.price != Decimal(mad.price)
                or set(rivals) != set(await lstat.rivals)
            ):
                lstat = await models.RaceStat.create(race=race, place=cur_plc, price=mad.price, premium=mad.premium)
                await lstat.rivals.add(*rivals)
            if not ads:
                await sleep(60)
                continue
            if not (cad := self.get_cad(ads, race.ceil, k, race.target_place, cur_plc)):
                continue
            new_price = Decimal(cad.price) - k * step(mad, cad, curex.cur.scale)
            if (
                Decimal(mad.price) == new_price and volume == last_vol
            ):  # Если место уже нужное или нужная цена и так уже стоит
                print(f"{'v' if taker_side else '^'}{mad.price}", end=f"[{race.ceil}+{cur_plc}] ", flush=True)
                await sleep(sleep_sec)
                continue
            if cad.priceType:  # Если цена конкурента плавающая, то повышаем себе не цену, а %
                new_premium = Decimal(cad.premium) - k * step(mad, cad, 2)
                if Decimal(mad.premium) == new_premium:  # Если нужный % и так уже стоит
                    if mad.priceType and cur_plc != race.target_place:
                        new_premium -= k * step(mad, cad, 2)
                    elif volume == last_vol:
                        print(end="v" if taker_side else "^", flush=True)
                        await sleep(sleep_sec)
                        continue
                mad.premium = new_premium.to_eng_string()
            mad.priceType = cad.priceType
            mad.quantity = volume
            mad.maxAmount = str(2_000_000)
            req = AdUpdateRequest.model_validate(
                {**mad.model_dump(), "price": new_price.to_eng_string(), "paymentIds": [str(p.exid) for p in creds]}
            )
            try:
                print(
                    f"c{race.ceil}+{cur_plc} {coinex.coin.ticker}{'-' if taker_side else '+'}{req.price}{curex.cur.ticker}"
                    f"{[pm.norm for pm in race.road.ad.pms]}{f'({req.premium}%)' if req.premium != '0' else ''} "
                    f"t{race.target_place} ;",
                    flush=True,
                )
                _res = self.ad_upd(req)
            except FailedRequestError as e:
                if ExcCode(e.status_code) == ExcCode.FixPriceLimit:
                    if limits := re.search(
                        r"The fixed price set is lower than ([0-9]+\.?[0-9]{0,2}) or higher than ([0-9]+\.?[0-9]{0,2})",
                        e.message,
                    ):
                        req.price = limits.group(1 if taker_side else 2)
                        if req.price != mad.price:
                            _res = self.ad_upd(req)
                    else:
                        raise e
                elif ExcCode(e.status_code) == ExcCode.InsufficientBalance:
                    asset = await models.Asset.get(addr__actor=self.actor, addr__coin_id=coinex.coin_id)
                    req.quantity = str(
                        round(asset.free - (asset.freeze or 0) - (asset.lock or 0), coinex.coin.scale or coinex.scale)
                    )
                    _res = self.ad_upd(req)
                elif ExcCode(e.status_code) == ExcCode.RareLimit:
                    sad = [
                        ma
                        for ma in self.my_ads(False)
                        if (
                            ma.currencyId == curex.exid
                            and ma.tokenId == coinex.exid
                            and taker_side == (not ma.side)
                            and ma.payments == [pe.exid for pe in pmexs]
                        )
                    ][0]
                    self.ad_del(ad_id=int(mad.id))
                    req.id = sad.id
                    req.actionType = "ACTIVE"
                    self.api.update_ad(**req.model_dump())
                    logging.warning(f"Ad#{mad.id} recreated")
                elif ExcCode(e.status_code) == ExcCode.Timestamp:
                    await sleep(3)
                else:
                    raise e
            except (ReadTimeoutError, ConnectionDoesNotExistError):
                logging.warning("Connection failed. Restarting..")
            await sleep(6)

    async def get_books(
        self, coinex: models.CoinEx, curex: models.CurEx, pmexs: list[models.PmEx]
    ) -> tuple[list[Ad], list[Ad]]:
        buy: list[Ad] = await self.ads(coinex, curex, False, pmexs, None, 30)
        sell: list[Ad] = await self.ads(coinex, curex, True, pmexs, None, 30)
        return buy, sell

    async def get_spread(
        self, bb: list[Ad], sb: list[Ad], perc: Decimal, vmf: bool = None, place: int = 0, exact: bool = False
    ) -> tuple[tuple[Decimal, Decimal], Decimal, bool, int]:
        buy_price, sell_price = Decimal(bb[place].price), Decimal(sb[place].price)
        half_spread = (buy_price - sell_price) / (buy_price + sell_price)
        if half_spread * 2 < perc:
            if not exact:
                if vmf is None:  # сначала фильтруем только VA
                    return await self.get_spread(bb, sb, perc, True, place)
                # если даже по VA не хватает спреда - увеличиваем место
                return await self.get_spread(bb, sb, perc, vmf, place + 1)

        return (buy_price, sell_price), half_spread, vmf, place

    async def get_ceils(
        self,
        coinex: models.CoinEx,
        curex: models.CurEx,
        pmexs: list[models.PmEx],
        min_prof=0.01,
        vmf: bool = False,
        place: int = 0,
    ) -> tuple[tuple[Decimal, Decimal], Decimal, bool, int]:  # todo: refact to Pairex
        min_prof = Decimal(min_prof)
        bb, sb = await self.get_books(coinex, curex, pmexs)
        if vmf:
            bb = [b for b in bb if "VA" in b.authTag]
            sb = [s for s in sb if "VA" in s.authTag]
        perc = pmexs[0].pm.fee + min_prof
        (bf, sf), hp, vmf, zplace = await self.get_spread(bb, sb, perc, vmf, place)
        mdl = (bf + sf) / 2
        bc, sc = mdl + mdl * (perc / 2), mdl - mdl * (perc / 2)
        return (bc, sc), hp, vmf, zplace

    async def parse_ads(
        self,
        coinex: models.CoinEx,
        curex: models.CurEx,
        taker_side: bool,
        pms: list[str] = None,
        ceil: float = None,
        volume: float = 9000,
        min_fiat: int = None,
        max_fiat: int = None,
    ):
        k = (-1) ** int(taker_side)  # on_buy=1, on_sell=-1

        if pms:
            creds: dict[models.PmEx, models.CredEx] = await self.get_credexs_by_norms(pms, curex.cur_id)
            [str(p.exid) for p in creds.values()]

            if taker_side:  # гонка в стакане продажи - мы покупаем монету за ФИАТ
                fiats = await models.Fiat.filter(
                    cred_id__in=[cx.cred_id for cx in creds.values()], amount__not=F("target")
                )
                volume = min(volume, max(fiats, key=lambda f: f.target - f.amount).amount / ceil)
            else:  # гонка в стакане покупки - мы продаем МОНЕТУ за фиат
                asset = await models.Asset.get(addr__actor=self.actor, addr__coin_id=coinex.coin_id)
                volume = min(volume, asset.free - (asset.freeze or 0) - (asset.lock or 0))
        volume = str(round(volume, coinex.coin.scale))
        ps = await PairSide.get(
            is_sell=taker_side,
            pair__coin_id=coinex.coin_id,
            pair__cur_id=curex.cur_id,
        )
        while self.actor.person.user.status > 0:  # todo: depends on rest asset/fiat
            ads: list[Ad] = await self.ads(coinex, curex, taker_side, pms and list(creds.keys()))

            if not ads:
                print(coinex.exid, curex.exid, taker_side, "no ads!")
                await sleep(300)
                continue

            for i, ad in enumerate(ads):
                if (ceil - float(ad.price)) * k < 0:
                    break
                if int(ad.userId) == self.actor.exid:
                    logging.info(f"My ad {'-' if taker_side else '+'}{coinex.exid}/{curex.exid} on place#{i}")
                    continue
                ad_db, isnew = await self.cond_upsert(ad, ps=ps)
                if isnew:
                    s = f"{'-' if taker_side else '+'}{ad.price}[{ad.minAmount}-{ad.maxAmount}]{coinex.exid}/{curex.exid}"
                    print(s, end=" | ", flush=True)
                try:
                    # take
                    ...
                except FailedRequestError as e:
                    if ExcCode(e.status_code) == ExcCode.RareLimit:
                        await sleep(195)
                    elif ExcCode(e.status_code) == ExcCode.Timestamp:
                        await sleep(2)
                    else:
                        raise e
                except (ReadTimeoutError, ConnectionDoesNotExistError):
                    logging.warning("Connection failed. Restarting..")
            await sleep(3)

    async def cond_upsert(
        self, ad: Ad, rname: str = None, ps: PairSide = None, force: bool = False
    ) -> tuple[models.Ad, bool]:
        _sim, cid = None, None
        ad_db = await models.Ad.get_or_none(exid=ad.id, maker__ex=self.ex_client.ex).prefetch_related("cond")
        # если точно такое условие уже есть в бд
        if not (cleaned := clean(ad.remark)) or (cid := {oc[0]: ci for ci, oc in self.all_conds.items()}.get(cleaned)):
            # и объява с таким ид уже есть, но у нее другое условие
            if ad_db and ad_db.cond_id != cid:
                # то обновляем ид ее условия
                ad_db.cond_id = cid
                await ad_db.save()
                logging.info(f"{ad.nickName} upd cond#{ad_db.cond_id}->{cid}")
                # old_cid = ad_db.cond_id # todo: solve race-condition, а пока что очищаем при каждом запуске
                # if not len((old_cond := await Cond.get(id=old_cid).prefetch_related('ads')).ads):
                #     await old_cond.delete()
                #     logging.warning(f"Cond#{old_cid} deleted!")
            return (ad_db or force and await self.ad_create(ad, cid, rname, ps)), False
        # если эта объява в таким ид уже есть в бд, но с другим условием (или без), а текущего условия еще нет в бд
        if ad_db:
            await ad_db.fetch_related("cond__ads", "maker")
            if not ad_db.cond_id or (
                # у измененного условия этой объявы есть другие объявы?
                (rest_ads := set(ad_db.cond.ads) - {ad_db})
                and
                # другие объявы этого условия принадлежат другим юзерам
                {ra.maker_id for ra in rest_ads} - {ad_db.maker_id}
            ):
                # создадим новое условие и присвоим его только текущей объяве
                cid = await self.cond_new(cleaned, {int(ad.userId)})
                ad_db.cond_id = cid
                await ad_db.save()

                return ad_db, True
            # а если других объяв со старым условием этой обявы нет, либо они все этого же юзера
            # обновляем условие (в тч во всех ЕГО объявах)
            ad_db.cond.last_ver = ad_db.cond.raw_txt
            ad_db.cond.raw_txt = cleaned
            await ad_db.cond.save()
            await self.cond_upd(ad_db.cond, {ad_db.maker.exid})
            # и подправим коэфициенты похожести нового текста
            await self.fix_rel_sims(ad_db.cond_id, cleaned)
            return ad_db, False

        cid = await self.cond_new(cleaned, {int(ad.userId)})
        return await self.ad_create(ad, cid, rname, ps), True

    async def cond_new(self, txt: str, uids: set[int]) -> int:
        new_cond, _ = await Cond.update_or_create(raw_txt=txt)
        # и максимально похожую связь для нового условия (если есть >= 60%)
        await self.cond_upd(new_cond, uids)
        return new_cond.id

    async def cond_upd(self, cond: Cond, uids: set[int]):
        self.all_conds[cond.id] = cond.raw_txt, uids
        # и максимально похожую связь для нового условия (если есть >= 60%)
        old_cid, sim = await self.cond_get_max_sim(cond.id, cond.raw_txt, uids)
        await self.actual_sim(cond.id, old_cid, sim)

    def find_in_tree(self, cid: int, old_cid: int) -> bool:
        if p := self.cond_sims.get(old_cid):
            if p == cid:
                return True
            return self.find_in_tree(cid, p)
        return False

    async def cond_get_max_sim(self, cid: int, txt: str, uids: set[int]) -> tuple[int | None, int | None]:
        # находим все старые тексты похожие на 90% и более
        if len(txt) < 15:
            return None, None
        sims: dict[int, int] = {}
        for old_cid, (old_txt, old_uids) in self.all_conds.items():
            if len(old_txt) < 15 or uids == old_uids:
                continue
            elif not self.can_add_sim(cid, old_cid):
                continue
            if sim := get_sim(txt, old_txt):
                sims[old_cid] = sim
        # если есть, берем самый похожий из них
        if sims:
            old_cid, sim = max(sims.items(), key=lambda x: x[1])
            await sleep(0.3)
            return old_cid, sim
        return None, None

    def can_add_sim(self, cid: int, old_cid: int) -> bool:
        if cid == old_cid:
            return False
        elif self.cond_sims.get(cid) == old_cid:
            return False
        elif self.find_in_tree(cid, old_cid):
            return False
        elif self.cond_sims.get(old_cid) == cid:
            return False
        elif cid in self.rcond_sims.get(old_cid, {}):
            return False
        elif old_cid in self.rcond_sims.get(cid, {}):
            return False
        return True

    async def person_upsert(self, name: str, exid: int) -> models.Person:
        if actor := await models.Actor.get_or_none(exid=exid, ex=self.ex_client.ex).prefetch_related("person"):
            if not actor.person:
                actor.person = await models.Person.create(name=name)
                await actor.save()
            return actor.person
        return await models.Person.create(name=name)

    async def ad_create(
        self, ad: Ad, cid: int = None, rname: str = None, ps: PairSide = None, actor: Actor = None
    ) -> models.Ad:
        act_df = {}
        if int(ad.userId) != self.actor.exid:
            act_df |= {"name": ad.nickName}
        if rname:
            act_df |= {"person": await self.person_upsert(rname, int(ad.userId))}
        if not actor:
            actor, _ = await Actor.update_or_create(act_df, exid=ad.userId, ex=self.ex_client.ex)
        ps = ps or await PairSide.get_or_none(
            is_sell=ad.side,
            pair__coin__ticker=ad.tokenId,
            pair__cur__ticker=ad.currencyId,
        ).prefetch_related("pair__cur", "pair__coin")
        if not ps or not ps.pair:
            ...  # THB/USDC
        ad_upd = models.Ad.validate(ad.model_dump(by_alias=True))
        cur_scale = 10**ps.pair.cur.scale
        df_unq = ad_upd.df_unq(
            maker_id=actor.id,
            pair_side_id=ps.id,
            amount=int(float(ad.quantity) * float(ad.price) * cur_scale),
            quantity=int(float(ad.quantity) * 10**ps.pair.coin.scale),
            min_fiat=int(float(ad.minAmount) * cur_scale),
            max_fiat=ad.maxAmount and int(float(ad.maxAmount) * cur_scale),
            price=int(float(ad.price) * cur_scale),
            premium=int(float(ad.premium) * cur_scale),
        )
        ad_db, _ = await models.Ad.update_or_create(**df_unq)
        await ad_db.pms.add(*(await models.Pm.filter(pmexs__ex=self.ex_client.ex, pmexs__exid__in=ad.payments)))
        return ad_db

    async def fix_rel_sims(self, cid: int, new_txt: str):
        for rel_sim in await CondSim.filter(cond_rel_id=cid).prefetch_related("cond"):
            if sim := get_sim(new_txt, rel_sim.cond.raw_txt):
                rel_sim.similarity = sim
                await rel_sim.save()
            else:
                await rel_sim.delete()

    async def actual_cond(self):
        for curr, old in await CondSim.all().values_list("cond_id", "cond_rel_id"):
            self.cond_sims[curr] = old
            self.rcond_sims[old] |= {curr}
        for cid, (txt, uids) in self.all_conds.items():
            old_cid, sim = await self.cond_get_max_sim(cid, txt, uids)
            await self.actual_sim(cid, old_cid, sim)
            # хз бля чо это ваще
            # for ad_db in await models.Ad.filter(direction__pairex__ex=self.ex_client.ex).prefetch_related("cond", "maker"):
            #     ad = Ad(id=str(ad_db.exid), userId=str(ad_db.maker.exid), remark=ad_db.cond.raw_txt)
            #     await self.cond_upsert(ad, force=True)

    async def actual_sim(self, cid: int, old_cid: int, sim: int):
        if not sim:
            return
        if old_sim := await CondSim.get_or_none(cond_id=cid):
            if old_sim.cond_rel_id != old_cid:
                if sim > old_sim.similarity:
                    logging.warning(f"R {cid}: {old_sim.similarity}->{sim} ({old_sim.cond_rel_id}->{old_cid})")
                    await old_sim.update_from_dict({"similarity": sim, "old_rel_id": old_cid}).save()
                    self._cond_sim_upd(cid, old_cid)
            elif sim != old_sim.similarity:
                logging.info(f"{cid}: {old_sim.similarity}->{sim}")
                await old_sim.update_from_dict({"similarity": sim}).save()
        else:
            await CondSim.create(cond_id=cid, cond_rel_id=old_cid, similarity=sim)
            self._cond_sim_upd(cid, old_cid)

    def _cond_sim_upd(self, cid: int, old_cid: int):
        if old_old_cid := self.cond_sims.get(cid):  # если старый cid уже был в дереве:
            self.rcond_sims[old_old_cid].remove(cid)  # удаляем из обратного
        self.cond_sims[cid] = old_cid  # а в прямом он автоматом переопределится, даже если и был
        self.rcond_sims[old_cid] |= {cid}  # ну и в обратное добавим новый

    async def get_credexs_by_pms(self, pms: list[models.Pm], cur_id: int) -> list[models.CredEx]:
        return await models.CredEx.filter(
            ex_id=self.actor.ex_id,
            cred__pmcur__pm_id__in=[pm.id for pm in pms],
            cred__person_id=self.actor.person_id,
            cred__pmcur__cur_id=cur_id,
        )

    def build_tree(self):
        set(self.cond_sims.keys()) | set(self.cond_sims.values())
        tree = defaultdict(dict)
        # Группируем родителей по детям
        for child, par in self.cond_sims.items():
            tree[par] |= {child: {}}  # todo: make from self.rcond_sim

        # Строим дерево снизу вверх
        def subtree(node):
            if not node:
                return node
            for key in node:
                subnode = tree.pop(key, {})
                d = subtree(subnode)
                node[key] |= d  # actual tree rebuilding here!
            return node  # todo: refact?

        # Находим корни / без родителей
        roots = set(self.cond_sims.values()) - set(self.cond_sims.keys())
        for root in roots:
            _ = subtree(tree[root])

        self.tree = tree


def get_sim(s1, s2) -> int:
    sim = int((SequenceMatcher(None, s1, s2).ratio() - 0.6) * 10_000)
    return sim if sim > 0 else 0


def detailed_diff(str1, str2):
    matcher = SequenceMatcher(None, str1, str2)
    result = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            result.append(str1[i1:i2])
        elif tag == "delete":
            result.append(f"[-{str1[i1:i2]}]")
        elif tag == "insert":
            result.append(f"[+{str2[j1:j2]}]")
        elif tag == "replace":
            result.append(f"[{str1[i1:i2]}→{str2[j1:j2]}]")

    return "".join(result)


def clean(s) -> str:
    clear = r"[^\w\s.,!?;:()\-]"
    repeat = r"(.)\1{2,}"
    s = re.sub(clear, "", s).lower()
    s = re.sub(repeat, r"\1", s)
    return s.replace("\n\n", "\n").replace("  ", " ").strip(" \n/.,!?-")


def step_is_need(mad, cad) -> bool:
    # todo: пока не решен непонятный кейс, почему то конкурент по всем параметрам слабже, но в списке ранжируется выше.
    #  текущая версия: recentExecuteRate округляется до целого, но на бэке его дробная часть больше
    return (
        bool(set(cad.authTag) & {"VA2", "BA"})
        or cad.recentExecuteRate > mad.recentExecuteRate
        or (
            cad.recentExecuteRate
            == mad.recentExecuteRate  # and cad.finishNum > mad.finishNum # пока прибавляем для равных
        )
    )


def step(mad, cad, scale: int = 2) -> Decimal:
    return Decimal(int(step_is_need(mad, cad)) * 10**-scale).__round__(scale)


class ExcCode(IntEnum):
    FixPriceLimit = 912120022
    RareLimit = 912120050
    InsufficientBalance = 912120024
    Timestamp = 10002
    IP = 10010
    Quantity = 912300019


async def main():
    logging.basicConfig(level=logging.INFO)
    _ = await init_db(TORM)

    @post_save(models.Race)
    async def race_upserted(
        _cls: type[models.Race], race: models.Race, created: bool, _db: BaseDBAsyncClient, _updated: list[str]
    ):
        logging.warning(f"Race {race.id} is now upserted")
        asyncio.all_tasks()
        if created:
            ...
        else:  # параметры гонки изменены
            ...

    actor = (
        await models.Actor.filter(ex_id=4, agent__isnull=False).prefetch_related("ex", "agent", "person__user").first()
    )
    async with FileClient(TOKEN) as b:
        b: FileClient
        # b.add_handler(MessageHandler(cond_start_handler, command("cond")))
        cl: AgentClient = actor.client(b)

        # await cl.ex_client.set_pairs()
        # await cl.ex_client.set_pms()
        # await cl.set_creds()
        # await cl.export_my_ads()

        # for name in names:
        #     s, _ = await models.Synonym.update_or_create(typ=SynonymType.name, txt=name)
        #     await s.curs.add(rub.cur)

        # пока порешали рейс-кондишн, очищаем сиротские условия при каждом запуске
        [await c.delete() for c in await Cond.filter(ads__isnull=True)]
        cl.all_conds = {
            c.id: (c.raw_txt, {a.maker.exid for a in c.ads}) for c in await Cond.all().prefetch_related("ads__maker")
        }
        for curr, old in await CondSim.filter().values_list("cond_id", "cond_rel_id"):
            cl.cond_sims[curr] = old
            cl.rcond_sims[old] |= {curr}

        cl.build_tree()
        a = set()

        def check_tree(tre):
            for p, c in tre.items():
                a.add(p)
                check_tree(c)

        for pr, ch in cl.tree.items():
            check_tree(ch)
        if ct := set(cl.tree.keys()) & a:
            logging.exception(f"cycle cids: {ct}")

        await cl.get_api_orders(159)

        races = await models.Race.filter(started=True).prefetch_related("road__ad__pair_side__pair", "road__ad__pms")
        tasks = [asyncio.create_task(cl.racing(race), name=f"Rc{race.id}") for race in races]
        # await cl.actual_cond()
        await gather(
            *tasks
            # cl.get_api_orders(),  # 10, 1738357200000, 1742504399999
            # cl.racing(usdt, rub, False, ["volet"], 83.88),  # гонка в стакане покупки - мы продаем
            # cl.racing(usdt, rub, True, ["volet"], 81.51),  # гонка в стакане продажи - мы покупаем
            # cl.racing(usdt, rub, False, ["payeer"], 81.49),  # гонка в стакане покупки - мы продаем
            # cl.racing(usdt, rub, True, ["payeer"], 80.7),  # гонка в стакане продажи - мы покупаем
            # cl.racing(eth, rub, False, ["volet"], 300_000),
            # cl.racing(eth, rub, True, ["volet"], 296_000),
            # cl.racing(eth, rub, False, ["payeer"], 300_000),
            # cl.racing(eth, rub, True, ["payeer"], 296_000),
            # cl.racing(btc, rub, False, ["volet"], 9_800_000),
            # cl.racing(btc, rub, True, ["volet"], 9_700_000),
            # cl.racing(btc, rub, False, ["payeer"], 9_800_000),
            # cl.racing(btc, rub, True, ["payeer"], 9_700_000),
            # cl.racing(usdc, rub, False, ["volet"], 80.98),
            # cl.racing(usdc, rub, True, ["volet"], 80.01),
            # cl.racing(usdc, rub, False, ["payeer"], 80.98),
            # cl.racing(usdc, rub, True, ["payeer"], 80.01),
            # cl.parse_ads(usdt, rub, False, ceil=81, volume=360),
            # cl.parse_ads(usdt, rub, True, ceil=80, volume=360),
        )

        # bor = BaseOrderReq(
        #     ad_id="1861440060199632896",
        #     # asset_amount=40,
        #     fiat_amount=3000,
        #     amount_is_fiat=True,
        #     is_sell=False,
        #     cur_exid=rub.exid,
        #     coin_exid=usdt.exid,
        #     coin_scale=usdt.coin.scale,
        # )
        # res: OrderResp = await cl.order_request(bor)
        # await cl.cancel_order(res.orderId)
        await cl.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down")
