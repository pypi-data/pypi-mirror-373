import time
import struct
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

# Генерируем ключи Ed25519
back_prv = ed25519.Ed25519PrivateKey.generate()
back_pub = back_prv.public_key()
sender_prv = ed25519.Ed25519PrivateKey.generate()
sender_pub = sender_prv.public_key()
sender_id = 2
receiver_id = 5
cur_id = 1


def transfer_pack(receiver: int, amount: int, cur: int, timestamp: int) -> bytes:
    """Упаковка транзакции в 18 байт без ид отправителя"""
    return struct.pack(">LQHL", receiver, amount, cur, timestamp)


# def create_proof(trans_packed: bytes, sender_signature: bytes) -> bytes:
#     """Создание доказательства транзакции (18 + 64 = 82 bytes)"""
#     # Добавляем подпись отправителя
#     data_with_sender_sig = trans_packed + sender_signature
#
#     print(f"DEBUG: Размер data_with_sender_sig: {len(data_with_sender_sig)} байт")
#
#     # Бэкенд подписывает весь пакет данных
#     backend_signature = back_prv.sign(data_with_sender_sig)
#
#     # Финальное доказательство
#     proof = data_with_sender_sig + backend_signature
#
#     print(f"DEBUG: Размер итогового proof: {len(proof)} байт")
#
#     return proof


# def verify_proof(proof: bytes, sender_public_key, backend_public_key) -> dict:
#     """Проверка компактного доказательства"""
#     try:
#         print(f"DEBUG: Размер после распаковки: {len(proof)} байт")
#
#         # Извлекаем базовые данные (4+8+2+4 = 18 байт)
#         receiver, amount, cur, timestamp = struct.unpack(">LQHL", proof[0:18])
#
#         # Извлекаем подпись отправителя
#         sender_signature = proof[18 : 18 + 64]
#
#         # Остальное - подпись бэкенда
#         backend_signature = proof[18 + 64 : 18 + 64 + 64]
#
#         print(f"DEBUG: Извлечены данные - receiver_id: {receiver}, amount: {amount}, cur_id: {cur}")
#         print(f"DEBUG: timestamp: {timestamp}")
#
#         # 1. Проверяем подпись бэкенда
#         compact_data = transfer_pack(receiver, amount, cur, timestamp)
#         data_with_sender_sig = compact_data + sender_signature
#         backend_public_key.verify(backend_signature, data_with_sender_sig)
#         print("DEBUG: Подпись бэкенда верна")
#
#         # 2. Проверяем подпись отправителя - используем оригинальную строку amount
#         sender_public_key.verify(sender_signature, compact_data)
#         print("DEBUG: Подпись отправителя верна!")
#
#         return {
#             "valid": True,
#             "transaction_details": {
#                 # "sender_id": sender_id,
#                 "receiver_id": receiver,
#                 "amount": amount,
#                 "cur_id": cur,
#                 "timestamp": timestamp,
#             },
#         }
#
#     except InvalidSignature as e:
#         print(f"DEBUG: InvalidSignature ошибка: {e}")
#         return {"valid": False, "error": f"Недействительная подпись: {str(e)}"}


def create_proof_minimal(receiver: int, amount: int, cur: int, timestamp: int, sender_signature: bytes) -> bytes:
    """Минимальное доказательство - только подписи"""
    trans_packed = transfer_pack(receiver, amount, cur, timestamp)

    # Только две подписи: отправителя + бэкенда (128 байт)
    backend_signature = back_prv.sign(trans_packed + sender_signature)

    return sender_signature + backend_signature


def verify_proof_minimal(
    proof: bytes,
    sender_public_key,
    backend_public_key,
    trans_packed: bytes,
) -> bool:
    """Проверка минимального доказательства"""
    try:
        if len(proof) != 128:  # 64 + 64
            return False  # wrong size

        sender_signature = proof[:64]
        backend_signature = proof[64:128]

        # 1. Проверяем подпись отправителя
        sender_public_key.verify(sender_signature, trans_packed)

        # 2. Проверяем подпись бэкенда
        backend_public_key.verify(backend_signature, trans_packed + sender_signature)

        return True

    except InvalidSignature:
        return False  # wring sign


def demo():
    print("=== Демонстрация оптимизированной системы доказательств ===\n")

    amount = 10050
    timestamp = int(time.time())

    print(f"Транзакция: {sender_id} → {receiver_id}: {amount}")

    # Отправитель подписывает транзакцию
    # transaction_hash = create_transaction_hash(sender_id, receiver_id, amount, timestamp)
    # print(f"DEBUG: Оригинальный transaction_hash (hex): {transaction_hash.hex()}")
    trans_packed = transfer_pack(receiver_id, amount, cur_id, timestamp)
    sender_signature = sender_prv.sign(trans_packed)
    print(f"DEBUG: Оригинальная sender_signature (hex): {sender_signature.hex()}")

    # Тестируем разные варианты доказательств
    print("\n📊 Сравнение размеров доказательств:")

    # # 1. Компактное доказательство
    # proof = create_proof(trans_packed, sender_signature)
    # result = verify_proof(proof, sender_pub, back_pub)
    # print(f"1. Компактное:        {len(proof):3d} байт - {'✅' if result['valid'] else '❌'}")
    # if not result["valid"]:
    #     print(f"   Ошибка: {result['error']}")

    # 3. Минимальное доказательство
    proof_minimal = create_proof_minimal(receiver_id, amount, cur_id, timestamp, sender_signature)
    result_minimal = verify_proof_minimal(proof_minimal, sender_pub, back_pub, trans_packed)
    print(f"3. Минимальное:       {len(proof_minimal):3d} байт - {'✅' if result_minimal else '❌'}")

    # Показываем детали лучшего варианта
    print(f"\n✨Минимальное доказательство ({len(proof_minimal)} байт):")
    print("   • Содержит только две подписи Ed25519")
    print("   • Требует знания деталей транзакции для проверки")
    print("   • Максимальное сжатие с zlib")


if __name__ == "__main__":
    demo()
