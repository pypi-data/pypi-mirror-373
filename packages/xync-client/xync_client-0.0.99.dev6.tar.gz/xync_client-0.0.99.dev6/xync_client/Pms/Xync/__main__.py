import time
from base64 import b64encode, b64decode
from uuid import UUID

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from tortoise import Tortoise, run_async
from x_model import init_db
from xync_client.loader import TORM, GP
from xync_schema.models import User, Cur, Transaction


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

    ts = int(time.time())
    gp = bytes.fromhex(GP)
    prv = Ed25519PrivateKey.from_private_bytes(gp)
    # === Генезис отправляет мне половины своих балансов ===
    rub_amount = int((await sender.balance(rub.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=rub.id, receiver_id=receiver.id, amount=rub_amount)), sender_id=sender.id
    )
    rub_uid = UUID(bytes=t.pack)
    be = b64encode(rub_uid.bytes)
    b64decode(be)
    sign = prv.sign(rub_uid.bytes)
    trans_rub = await sender.send(rub_uid, **tcra, sign=sign)
    # Валидатор аппрувит транзакцию
    await trans_rub.approve(gp)
    # Получатель проверяет доказательство
    trans_rub.check(prv.public_key().public_bytes_raw())

    usd_amount = int((await sender.balance(usd.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=usd.id, receiver_id=receiver.id, amount=usd_amount)), sender_id=sender.id
    )
    usd_uid = UUID(bytes=t.pack)
    sign = prv.sign(usd_uid.bytes)
    trans_usd = await sender.send(usd_uid, **tcra, sign=sign)
    await trans_usd.approve(gp)
    trans_usd.check(prv.public_key().public_bytes_raw())

    eur_amount = int((await sender.balance(eur.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=eur.id, receiver_id=receiver.id, amount=eur_amount)), sender_id=sender.id
    )
    eur_uid = UUID(bytes=t.pack)
    sign = prv.sign(eur_uid.bytes)
    trans_eur = await sender.send(eur_uid, **tcra, sign=sign)
    await trans_eur.approve(gp)
    trans_eur.check(prv.public_key().public_bytes_raw())

    hkd_amount = int((await sender.balance(hkd.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=hkd.id, receiver_id=receiver.id, amount=hkd_amount)), sender_id=sender.id
    )
    hkd_uid = UUID(bytes=t.pack)
    sign = prv.sign(hkd_uid.bytes)
    trans_hkd = await sender.send(hkd_uid, **tcra, sign=sign)
    await trans_hkd.approve(gp)
    trans_hkd.check(prv.public_key().public_bytes_raw())

    cny_amount = int((await sender.balance(cny.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=cny.id, receiver_id=receiver.id, amount=cny_amount)), sender_id=sender.id
    )
    cny_uid = UUID(bytes=t.pack)
    sign = prv.sign(cny_uid.bytes)
    trans_cny = await sender.send(cny_uid, **tcra, sign=sign)
    await trans_cny.approve(gp)
    trans_cny.check(prv.public_key().public_bytes_raw())

    aed_amount = int((await sender.balance(aed.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=aed.id, receiver_id=receiver.id, amount=aed_amount)), sender_id=sender.id
    )
    aed_uid = UUID(bytes=t.pack)
    sign = prv.sign(aed_uid.bytes)
    trans_aed = await sender.send(aed_uid, **tcra, sign=sign)
    await trans_aed.approve(gp)
    trans_aed.check(prv.public_key().public_bytes_raw())

    thb_amount = int((await sender.balance(thb.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=thb.id, receiver_id=receiver.id, amount=thb_amount)), sender_id=sender.id
    )
    thb_uid = UUID(bytes=t.pack)
    sign = prv.sign(thb_uid.bytes)
    trans_thb = await sender.send(thb_uid, **tcra, sign=sign)
    await trans_thb.approve(gp)
    trans_thb.check(prv.public_key().public_bytes_raw())

    idr_amount = int((await sender.balance(idr.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=idr.id, receiver_id=receiver.id, amount=idr_amount)), sender_id=sender.id
    )
    idr_uid = UUID(bytes=t.pack)
    sign = prv.sign(idr_uid.bytes)
    trans_idr = await sender.send(idr_uid, **tcra, sign=sign)
    await trans_idr.approve(gp)
    trans_idr.check(prv.public_key().public_bytes_raw())

    tl_amount = int((await sender.balance(tl.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=tl.id, receiver_id=receiver.id, amount=tl_amount)), sender_id=sender.id
    )
    tl_uid = UUID(bytes=t.pack)
    sign = prv.sign(tl_uid.bytes)
    trans_tl = await sender.send(tl_uid, **tcra, sign=sign)
    await trans_tl.approve(gp)
    trans_tl.check(prv.public_key().public_bytes_raw())

    gel_amount = int((await sender.balance(gel.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=gel.id, receiver_id=receiver.id, amount=gel_amount)), sender_id=sender.id
    )
    gel_uid = UUID(bytes=t.pack)
    sign = prv.sign(gel_uid.bytes)
    trans_gel = await sender.send(gel_uid, **tcra, sign=sign)
    await trans_gel.approve(gp)
    trans_gel.check(prv.public_key().public_bytes_raw())

    vnd_amount = int((await sender.balance(vnd.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=vnd.id, receiver_id=receiver.id, amount=vnd_amount)), sender_id=sender.id
    )
    vnd_uid = UUID(bytes=t.pack)
    sign = prv.sign(vnd_uid.bytes)
    trans_vnd = await sender.send(vnd_uid, **tcra, sign=sign)
    await trans_vnd.approve(gp)
    trans_vnd.check(prv.public_key().public_bytes_raw())

    php_amount = int((await sender.balance(php.id)) * 0.5)
    t = Transaction(
        **(tcra := dict(ts=ts, cur_id=php.id, receiver_id=receiver.id, amount=php_amount)), sender_id=sender.id
    )
    php_uid = UUID(bytes=t.pack)
    sign = prv.sign(php_uid.bytes)
    trans_php = await sender.send(php_uid, **tcra, sign=sign)
    await trans_php.approve(gp)
    trans_php.check(prv.public_key().public_bytes_raw())

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
