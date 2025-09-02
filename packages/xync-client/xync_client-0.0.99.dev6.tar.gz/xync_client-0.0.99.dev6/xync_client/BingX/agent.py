from xync_client.Abc.Agent import BaseAgentClient
from xync_schema.pydantic import FiatNew
from xync_schema.models import Cur, Fiat
from xync_client.Abc.Base import DictOfDicts
from xync_schema.models import Coin, OrderStatus


class AgentClient(BaseAgentClient):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "app_version": "9.2.5",
        "appid": "30004",
        "appsiteid": "0",
        "authorization": "Bearer eyJicyI6MCwiYWlkIjoxMDAwOSwicGlkIjoiMzAiLCJzaWQiOiJhM2JmYWE4MzFiOWUxYzc5MGJjYjBkYmNjMjM3YTFmMiIsImFsZyI6IkhTNTEyIn0.eyJzdWIiOiIxMzc5MzM1NzcyNDUxNDk1OTQxIiwiZXhwIjoxNzM3NDcyMjE1LCJqdGkiOiI4OWViMjEzOC1lYzQ2LTQ2YjctODIyYi1mZDg0ZmYxMjM4ZmMifQ.AMV6qqB0XI84xDc7VnG3ua27Q7o_nMrJbTsG4JrGWfa-yVi7-fxEwo_LA4d0RNueS355egXl33j--Q6_UUf74w",
        "channel": "official",
        "device_brand": "Linux_Chrome_131.0.0.0",
        "device_id": "6f76e02b64ba4a078a331eb5c323913b",
        "lang": "ru-RU",
        "mainappid": "10009",
        "origin": "https://bingx.paycat.com",
        "platformid": "30",
        "priority": "u=1, i",
        "referer": "https://bingx.paycat.com/",
        "reg_channel": "official",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sign": "633C6C2E893168F3840D61D1C0F0161E390F67FB34D3E121F12848A35805A8B1",
        "timestamp": "1737040244016",
        "timezone": "3",
        "traceid": "e355ec5e01b34d94aabcffb45d13eff5",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    # 0: Получшение заявок за заданное время, в статусе, по валюте, монете
    async def get_orders(
        self, status: OrderStatus = OrderStatus.created, coin: Coin = None, cur: Cur = None, is_sell: bool = None
    ):
        params = {
            "pageId": "0",
            "pageSize": "10",
            "messageStatus": "0",
            "orderType": "1",
            "orderStatus": "",
            "fiat": "",
            "searchKeyword": "",
            "tradeType": "",
            "beginTime": "1706475600000",
            "endTime": "1738184399999",
        }
        order = await self._get("/api/c2c/v2/order/list", params=params)
        return order["data"]["result"]

    # 1: [T] Запрос на старт сделки
    async def order_request(self, ad_id: int, amount: float):
        json_data = {
            "advertNo": f"{ad_id}",
            "asset": "USDT",
            "fiat": "RUB",
            "type": 1,
            "userPrice": 103,
            "areaType": 2,
            "amount": f"{amount}",
            "paymentMethodId": 110,
        }
        order = await self._post("/api/c2c/v1/order/create", json=json_data)
        if order["data"]:
            return "SUCCESS"

    # 25: Список реквизитов моих платежных методов
    async def my_fiats(self, cur: Cur = None) -> DictOfDicts:
        re = await self._get("/api/c2c/v1/user-pay-method/list")
        return {fiats["id"]: fiats for fiats in re["data"]["payments"]}

    # 26: Создание реквизита моего платежного метода
    async def fiat_new(self, fiat: FiatNew) -> Fiat:
        pass

    # 27: Редактирование реквизита моего платежного метода
    async def fiat_upd(self):
        pass

    # 28: Удаление реквизита моего платежного метода
    async def fiat_del(self):
        pass

    # 29: Список моих объявлений
    async def my_ads(self):
        pass

    # 30: Создание объявления
    async def ad_new(self):
        pass

    # 31: Редактирование объявления
    async def ad_upd(self):
        pass

    # 32: Удаление
    async def ad_del(self):
        pass

    # 33: Вкл/выкл объявления
    async def ad_switch(self):
        pass
