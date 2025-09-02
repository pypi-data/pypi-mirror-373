import subprocess
from datetime import datetime
from json import dumps
from os.path import dirname
from uuid import uuid4

from x_client.aiohttp import Client as HttpClient


class BaseBingXClient(HttpClient):
    def _prehook(self, _payload: dict = None):
        traceid = str(uuid4()).replace("-", "")
        now = str(int(datetime.now().timestamp() * 1000))
        payload = dumps(_payload, separators=(",", ":"), sort_keys=True) if _payload else "{}"
        p = subprocess.Popen(["node", dirname(__file__) + "/req.mjs", now, traceid, payload], stdout=subprocess.PIPE)
        sign = p.stdout.read().decode().strip()
        return {
            "sign": sign,
            "timestamp": now,
            "traceid": traceid,
        }
