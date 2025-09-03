from enum import IntEnum
from time import sleep

import pyotp
from x_client.http import Client

from xync_client.loader import BYT2FA


class NoMakerException(Exception):
    pass


class AdsStatus(IntEnum):
    REST = 0
    WORKING = 1


class BybitP2P(Client):  # Bybit client
    host = "api2.bybit.com"

    pub_header = {"cookie": ";"}  # rewrite token for public methods

    last_ad_id: list[str] = []
    create_ad_body = {
        "priceType": "1",
        "premium": "119",
        "quantity": "0.01",
        "minAmount": "500",
        "maxAmount": "3500",
        "paymentPeriod": "15",
        "remark": "",
        "price": "",
        "paymentIds": ["3162981"],
        "tradingPreferenceSet": {
            "isKyc": "1",
            "hasCompleteRateDay30": "0",
            "completeRateDay30": "",
            "hasOrderFinishNumberDay30": "0",
            "orderFinishNumberDay30": "",
            "isMobile": "0",
            "isEmail": "0",
            "hasUnPostAd": "0",
            "hasRegisterTime": "0",
            "registerTimeThreshold": "",
            "hasNationalLimit": "0",
            "nationalLimit": "",
        },
        "tokenId": "ETH",
        "currencyId": "RUB",
        "side": "1",
        "securityRiskToken": "",
    }
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

    """ PUBLIC METHS """

    def get_ads(self, coin: str, cur: str, sell: bool = False, amount: int = None, payment: list[str] = None) -> list:
        data = {
            "userId": "",
            "tokenId": coin,
            "currencyId": cur,
            "payment": payment or [],
            "side": "0" if sell else "1",
            "size": "10",
            "page": "1",
            "amount": str(amount) if amount else "",
            "authMaker": False,
            "canTrade": False,
        }
        ads = self._post("/fiat/otc/item/online/", data, self.pub_header)
        return ads["result"]["items"]

    def get_config(self):
        resp = self._get("/fiat/p2p/config/initial", self.pub_header)
        return resp["result"]  # todo: tokens, pairs, ...

    def get_currencies(self):
        config = self.get_config()
        return config["symbols"]

    def get_coins(self):
        coins = self._get("/spot/api/basic/symbol_list", self.pub_header)
        return coins

    def get_payment_methods(self):
        pms = self._post("/fiat/otc/configuration/queryAllPaymentList/", headers=self.pub_header)
        return pms

    """ Private METHs"""

    def create_payment_method(self, payment_type: int, real_name: str, account_number: str) -> dict:
        method1 = self._post(
            "/fiat/otc/user/payment/new_create",
            {"paymentType": payment_type, "realName": real_name, "accountNo": account_number, "securityRiskToken": ""},
        )
        if srt := method1["result"]["securityRiskToken"]:
            self.check_2fa(srt)
            method2 = self._post(
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
            print(method1)

    def get_payment_method(self, fiat_id: int = None) -> dict:
        list_methods = self.get_user_pay_methods()
        if fiat_id:
            fiat = [m for m in list_methods if m["id"] == fiat_id][0]
            return fiat
        return list_methods[1]

    def update_payment_method(self, real_name: str, account_number: str, fiat_id: int = None) -> dict:
        fiat = self.get_payment_method(fiat_id)
        fiat["realName"] = real_name
        fiat["accountNo"] = account_number
        result = self._post("/fiat/otc/user/payment/new_update", fiat)
        srt = result["result"]["securityRiskToken"]
        self.check_2fa(srt)
        fiat["securityRiskToken"] = srt
        result2 = self._post("/fiat/otc/user/payment/new_update", fiat)
        return result2

    def delete_payment_method(self, ids: str) -> dict:
        data = {"id": ids, "securityRiskToken": ""}
        method = self._post("/fiat/otc/user/payment/new_delete", data)
        srt = method["result"]["securityRiskToken"]
        self.check_2fa(srt)
        data["securityRiskToken"] = srt
        delete = self._post("/fiat/otc/user/payment/new_delete", data)
        return delete

    def switch_ads(self, new_status: AdsStatus) -> dict:
        data = {"workStatus": new_status.name}
        res = self._post("/fiat/otc/maker/work-config/switch", data)
        return res

    def online_ads(self) -> str:
        online = self._get("/fiat/otc/maker/work-config/get")
        return online["result"]["workStatus"]

    @staticmethod
    def get_rate(list_ads: list) -> float:
        ads = [ad for ad in list_ads if set(ad["payments"]) - {"5", "51"}]
        return float(ads[0]["price"])

    def get_user_pay_methods(self):
        upm = self._post("/fiat/otc/user/payment/list")
        return upm["result"]

    def get_user_ads(self, active: bool = True) -> list:
        uo = self._post("/fiat/otc/item/personal/list", {"page": "1", "size": "10", "status": "2" if active else "0"})
        return uo["result"]["items"]

    def get_security_token_create(self):
        data = self._post("/fiat/otc/item/create", self.create_ad_body)
        if data["ret_code"] == 912120019:  # Current user can not to create add as maker
            raise NoMakerException(data)
        security_risk_token = data["result"]["securityRiskToken"]
        return security_risk_token

    def check_2fa(self, risk_token):
        # 2fa code
        bybit_secret = BYT2FA
        totp = pyotp.TOTP(bybit_secret)
        totp_code = totp.now()

        res = self._post(
            "/user/public/risk/verify", {"risk_token": risk_token, "component_list": {"google2fa": totp_code}}
        )
        if res["ret_msg"] != "success":
            print("Wrong 2fa, wait 5 secs and retry..")
            sleep(5)
            self.check_2fa(risk_token)
        return res

    def post_ad(self, risk_token: str):
        self.create_ad_body.update({"securityRiskToken": risk_token})
        data = self._post("/fiat/otc/item/create", self.create_ad_body)
        return data

    # создание объявлений
    def post_create_ad(self, token: str):
        result_check_2fa = self.check_2fa(token)
        assert result_check_2fa["ret_msg"] == "success", "2FA code wrong"

        result_add_ad = self._post_ad(token)
        if result_add_ad["ret_msg"] != "SUCCESS":
            print("Wrong 2fa on Ad creating, wait 9 secs and retry..")
            sleep(9)
            return self._post_create_ad(token)
        self.last_ad_id.append(result_add_ad["result"]["itemId"])

    def get_security_token_update(self) -> str:
        self.update_ad_body["id"] = self.last_ad_id
        data = self._post("/fiat/otc/item/update", self.update_ad_body)
        security_risk_token = data["result"]["securityRiskToken"]
        return security_risk_token

    def post_update_ad(self, token):
        result_check_2fa = self.check_2fa(token)
        assert result_check_2fa["ret_msg"] == "success", "2FA code wrong"

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

    def delete_ad(self, ad_id: str):
        data = self._post("/fiat/otc/item/cancel", {"itemId": ad_id})
        return data

    def create_order_taker(
        self, item_id: str, coin: str, cur: str, sell: bool, quantity: str, amount: float, cur_price: str
    ):
        data = self._post(
            "/fiat/otc/order/create",
            json={
                "itemId": item_id,
                "tokenId": coin,
                "currencyId": cur,
                "side": "0" if sell else "1",
                "quantity": quantity,
                "amount": amount,
                "curPrice": cur_price,
                "flag": "amount",
                "version": "1.0",
                "securityRiskToken": "",
            },
        )
        return data["result"]["securityRiskToken"]

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
