from xync_schema.models import Order

from xync_client.Abc.Order import BaseOrderClient


class OrderClient(BaseOrderClient):
    # 2: Отмена своего запроса на сделку
    async def cancel_request(self) -> Order: ...

    # 3: Одобрить запрос на сделку
    async def accept_request(self) -> bool: ...

    # 4: Отклонить чужой запрос на сделку
    async def reject_request(self) -> bool: ...

    # 5: Перевод сделки в состояние "оплачено", c отправкой чека
    async def mark_payed(self, receipt): ...

    # 6: Отмена одобренной сделки
    async def cancel_order(self) -> bool: ...

    # 7: Подтвердить получение оплаты
    async def confirm(self) -> bool: ...

    # 9, 10: Подать аппеляцию cо скриншотом/видео/файлом
    async def start_appeal(self, file) -> bool: ...

    # 11, 12: Встречное оспаривание полученной аппеляции cо скриншотом/видео/файлом
    async def dispute_appeal(self, file) -> bool: ...

    # 15: Отмена аппеляции
    async def cancel_appeal(self) -> bool: ...

    # 16: Отправка сообщения юзеру в чат по ордеру с приложенным файлом
    async def send_order_msg(self, msg: str, file=None) -> bool: ...

    # 17: Отправка сообщения по апелляции
    async def send_appeal_msg(self, file, msg: str = None) -> bool: ...

    # Загрузка файла
    async def _upload_file(self, order_id: int, path_to_file: str): ...
