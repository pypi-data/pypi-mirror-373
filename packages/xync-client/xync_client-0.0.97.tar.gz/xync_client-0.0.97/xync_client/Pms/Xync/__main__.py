import time
from tortoise import Tortoise, run_async
from x_model import init_db
from xync_client.loader import TORM
from xync_schema.models import User, Cur


# Демонстрация использования
async def init():
    _ = await init_db(TORM)

    sender: User = await User[0]
    receiver: User = await User[1]
    # Параметры транзакций
    rub = await Cur.get(ticker="RUB")
    usd = await Cur.get(ticker="USD")
    eur = await Cur.get(ticker="EUR")
    hkd = await Cur.get(ticker="HKD")
    cny = await Cur.get(ticker="CNY")
    aed = await Cur.get(ticker="AED")
    thb = await Cur.get(ticker="THB")
    idr = await Cur.get(ticker="IDR")
    tl = await Cur.get(ticker="TRY")
    gel = await Cur.get(ticker="GEL")
    vnd = await Cur.get(ticker="VND")
    php = await Cur.get(ticker="PHP")
    int(time.time())

    # === Генезис отправляет мне половины своих балансов ===
    trans_rub = await sender.send(int((await sender.balance(rub.id)) * 0.5), rub.id, receiver.id)
    trans_usd = await sender.send(int((await sender.balance(usd.id)) * 0.5), usd.id, receiver.id)
    trans_eur = await sender.send(int((await sender.balance(eur.id)) * 0.5), eur.id, receiver.id)
    trans_hkd = await sender.send(int((await sender.balance(hkd.id)) * 0.5), hkd.id, receiver.id)
    trans_cny = await sender.send(int((await sender.balance(cny.id)) * 0.5), cny.id, receiver.id)
    trans_aed = await sender.send(int((await sender.balance(aed.id)) * 0.5), aed.id, receiver.id)
    trans_thb = await sender.send(int((await sender.balance(thb.id)) * 0.5), thb.id, receiver.id)
    trans_idr = await sender.send(int((await sender.balance(idr.id)) * 0.5), idr.id, receiver.id)
    trans_tl = await sender.send(int((await sender.balance(tl.id)) * 0.5), tl.id, receiver.id)
    trans_gel = await sender.send(int((await sender.balance(gel.id)) * 0.5), gel.id, receiver.id)
    trans_vnd = await sender.send(int((await sender.balance(vnd.id)) * 0.5), vnd.id, receiver.id)
    trans_php = await sender.send(int((await sender.balance(php.id)) * 0.5), php.id, receiver.id)

    # Валидатор аппрувит транзакцию
    await trans_rub.vld_sign()
    await trans_usd.vld_sign()
    await trans_eur.vld_sign()
    await trans_hkd.vld_sign()
    await trans_cny.vld_sign()
    await trans_aed.vld_sign()
    await trans_thb.vld_sign()
    await trans_idr.vld_sign()
    await trans_tl.vld_sign()
    await trans_gel.vld_sign()
    await trans_vnd.vld_sign()
    await trans_php.vld_sign()

    # Получатель проверяет доказательство
    _res = trans_rub.check()
    _res = trans_usd.check()
    _res = trans_eur.check()
    _res = trans_hkd.check()
    _res = trans_cny.check()
    _res = trans_aed.check()
    _res = trans_thb.check()
    _res = trans_idr.check()
    _res = trans_tl.check()
    _res = trans_gel.check()
    _res = trans_vnd.check()
    _res = trans_php.check()

    # === СЦЕНАРИЙ 2: Общий запрос денег ===
    # print("\n=== СЦЕНАРИЙ 2: Общий запрос денег ===")
    # print(f"Получатель {receiver.id} создает общий запрос на {amount} (от любого отправителя)")
    #
    # # Получатель создает общий запрос денег
    # req: Transaction = await receiver.req(2050, rub.id)
    # print(f"5. Получатель создал общий запрос: ID {req.id}")
    #
    # # Отправитель подписывает транзакцию по запросу
    # trans_by_req = await sender.send_by_req(req)
    # print("6. Отправитель подписал транзакцию по общему запросу")
    #
    # # Получатель проверяет доказательство по запросу
    # trans_by_req.check()
    #
    # # === СЦЕНАРИЙ 3: Личный запрос денег ===
    # print("\n=== СЦЕНАРИЙ 3: Личный запрос денег ===")
    # print(f"Получатель {receiver.id} создает личный запрос для отправителя {sender.id}")
    #
    # # Получатель создает личный запрос денег
    # pers_req: Transaction = await receiver.req(3099, rub.id, sender.id)
    # print(f"9. Получатель создал личный запрос: ID {pers_req.id} для {sender.id}")
    #
    # # Отправитель подписывает транзакцию по личному запросу
    # await sender.send_by_req(pers_req)
    # # wrong_sender_trans = await validator.send_by_req(pers_req)
    # print("10. Отправитель подписал транзакцию по личному запросу")
    #
    # # Проверка: повторная оплата запроса
    # print("\n12. Попытка повторной оплаты уже оплаченного запроса:")
    # try:
    #     ...
    #     print("    ❌ Ошибка: бэкенд не должен был создать доказательство")
    # except ValueError as e:
    #     print(f"    ✅ Бэкенд корректно отклонил повторную оплату: {e}")

    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(init())
