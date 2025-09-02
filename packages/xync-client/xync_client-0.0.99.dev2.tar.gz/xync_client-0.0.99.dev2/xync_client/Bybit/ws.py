import hmac
import json
import websockets
from time import time


async def pub():
    async with websockets.connect("wss://stream.bybit.com/v5/public/spot") as websocket:
        sub_msg = json.dumps(
            {"op": "subscribe", "req_id": "1", "args": ["tickers.BTCUSDT", "tickers.ETHUSDT", "tickers.TONUSDT"]}
        )
        await websocket.send(sub_msg)
        p = {}
        while resp := await websocket.recv():
            if data := json.loads(resp).get("data"):
                p[data["symbol"]] = data["lastPrice"]
                print(f"BTC: {p.get('BTCUSDT')}\nETH: {p.get('ETHUSDT')}\nTON: {p.get('TONUSDT')}", end="\033[F\033[F")


async def priv(key: str, sec: str):
    async with websockets.connect("wss://stream.bybit.com/v5/private") as websocket:
        expires = int((time() + 5) * 1000)
        # Generate signature.
        signature = str(
            hmac.new(bytes(sec, "utf-8"), bytes(f"GET/realtime{expires}", "utf-8"), digestmod="sha256").hexdigest()
        )
        auth_msg = json.dumps({"op": "auth", "args": [key, expires, signature]})
        await websocket.send(auth_msg)
        await websocket.send(json.dumps({"req_id": "100001", "op": "ping"}))
        sub_msg = json.dumps({"op": "subscribe", "args": ["wallet"]})
        await websocket.send(sub_msg)
        while resp := await websocket.recv():
            if data := json.loads(resp).get("data"):
                print(data)
