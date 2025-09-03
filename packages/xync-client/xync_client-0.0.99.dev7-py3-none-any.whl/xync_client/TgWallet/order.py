from enum import StrEnum

from xync_schema.models import Order, OrderStatus

from xync_client.Abc.Order import BaseOrderClient


class Exceptions(StrEnum):
    PM_KYC = "OFFER_FIAT_COUNTRY_NOT_SUPPORTED_BY_USER_KYC_COUNTRY"


class OrderClient(BaseOrderClient):
    type_map = {
        OrderStatus.deleted: "CANCELLED",
        OrderStatus.created: "ACTIVE",
        OrderStatus.appealable: "ACTIVE",
        OrderStatus.canceled: "COMPLETED",
        OrderStatus.completed: "COMPLETED",
        OrderStatus.appealed_by_buyer: "ACTIVE",
        OrderStatus.appealed_by_seller: "ACTIVE",
        OrderStatus.buyer_appeal_disputed_by_seller: "ACTIVE",
        OrderStatus.paid: "COMPLETED",
        OrderStatus.rejected: "CANCELLED",
        OrderStatus.request_canceled: "CANCELLED",
        OrderStatus.requested: "ACTIVE",
        OrderStatus.seller_appeal_disputed_by_buyer: "ACTIVE",
    }

    # 2: Отмена своего запроса на сделку
    async def cancel_request(self) -> Order:
        typ = "seller" if self.im_seller else "buyer"
        cancel = await self._post(f"/p2p/public-api/v2/offer/order/cancel/by-{typ}", {"orderId": self.order.id})
        return cancel

    # 3: Одобрить запрос на сделку
    async def accept_request(self) -> bool:
        approve = await self._post(
            "/p2p/public-api/v2/offer/order/accept",
            {"orderId": self.order.id, "type": {True: "SALE", False: "BUY"}[self.im_seller]},
        )
        return approve

    # 4: Отклонить чужой запрос на сделку
    async def reject_request(self) -> bool:
        typ = "seller" if self.im_seller else "buyer"
        reject = await self._post(f"/p2p/public-api/v2/offer/order/cancel/by-{typ}", {"orderId": self.order.id})
        return reject

    # 5: Перевод сделки в состояние "оплачено", c отправкой чека
    async def mark_payed(self, receipt):
        paid = await self._post(
            "/p2p/public-api/v2/offer/order/confirm-sending-payment",
            {"orderId": self.order.id, "paymentReceipt": receipt},
        )
        return paid

    # 6: Отмена одобренной сделки
    async def cancel_order(self) -> bool:
        cancel = await self._post("/p2p/public-api/v2/offer/order/cancel/by-buyer", {"orderId": self.order.id})
        return cancel

    # 7: Подтвердить получение оплаты
    async def confirm(self) -> bool:
        payment_confirm = await self._post("/p2p/public-api/v2/payment-details/confirm", {"orderId": self.order.id})
        return payment_confirm

    # 9, 10: Подать аппеляцию cо скриншотом/видео/файлом
    async def start_appeal(self, file) -> bool:
        pass

    # 11, 12: Встречное оспаривание полученной аппеляции cо скриншотом/видео/файлом
    async def dispute_appeal(self, file) -> bool:
        pass

    # 15: Отмена аппеляции
    async def cancel_appeal(self) -> bool:
        pass

    # 16: Отправка сообщения юзеру в чат по ордеру с приложенным файлом
    async def send_order_msg(self, msg: str, file=None) -> bool:
        pass

    # 17: Отправка сообщения по апелляции
    async def send_appeal_msg(self, file, msg: str = None) -> bool:
        pass

    # Загрузка файла
    async def _upload_file(self, order_id: int, path_to_file: str):
        url = f"/public-api/v2/file-storage/file/upload?orderId={order_id}&uploadType=UPLOAD_BUYER_PAYMENT_RECEIPT"
        data = {"file": open(path_to_file, "rb")}
        upload_file = await self._post(url, data)
        return upload_file
