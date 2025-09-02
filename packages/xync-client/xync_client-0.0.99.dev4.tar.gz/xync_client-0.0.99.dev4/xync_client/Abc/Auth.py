import logging
from abc import abstractmethod

from aiohttp import ClientResponse
from aiohttp.http_exceptions import HttpProcessingError
from x_client.aiohttp import Client as HttpClient
from xync_schema.models import Actor


class BaseAuthClient(HttpClient):
    actor: Actor = None

    @abstractmethod
    async def _get_auth_hdrs(self) -> dict[str, str]: ...

    async def login(self) -> None:
        auth_hdrs: dict[str, str] = await self._get_auth_hdrs()
        # noinspection PyUnresolvedReferences
        self.session.headers.update(auth_hdrs)

    async def _post(self, url: str, data: dict = None, data_key: str = None, headers: dict = None):
        dt = {"json" if isinstance(data, dict) else "data": data}
        # noinspection PyUnresolvedReferences
        hdrs = {**self._prehook(data), **(headers or {})}
        resp = await self.session.post(url, **dt, headers=hdrs)
        return await self._proc(resp, data_key, data)

    async def _proc(self, resp: ClientResponse, data_key: str = None, body: dict | str = None) -> dict | str:
        try:
            # noinspection PyUnresolvedReferences
            return await super()._proc(resp, data_key)
        except HttpProcessingError as e:
            if e.code == 401:
                logging.warning(e)
                await self.login()
                # noinspection PyUnresolvedReferences
                res = await self.METHS[resp.method](self, resp.url.path, body, data_key=data_key)
                return res
