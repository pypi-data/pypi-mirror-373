from asyncio import run
from urllib.parse import parse_qs

from pyro_client.client.user import UserClient
from pyrogram.raw import functions
from pyrogram.raw.types import InputPeerSelf
from x_model import init_db

from xync_client.loader import PG_DSN
from xync_schema import models
from xync_schema.models import Actor


class WalletAuthClient(UserClient):
    async def get_init_data(self) -> dict:
        async with self:
            bot = await self.resolve_peer("wallet")
            res = await self.invoke(functions.messages.RequestWebView(peer=InputPeerSelf(), bot=bot, platform="ios"))
            raw = parse_qs(res.url)["tgWebAppUserId"][0].split("#tgWebAppData=")[1]
            j = parse_qs(raw)
            return {
                "web_view_init_data": {
                    "query_id": j["query_id"][0],
                    "user": j["user"][0],
                    "auth_date": j["auth_date"][0],
                    "hash": j["hash"][0],
                },
                "web_view_init_data_raw": raw,
                "ep": "menu",
            }


async def main():
    from xync_schema import TORM

    _ = await init_db(TORM, True)
    actor: Actor = (
        await Actor.filter(agent__isnull=False, ex__name="TgWallet").prefetch_related("ex", "person__user").first()
    )
    pcl = WalletAuthClient(actor.person.user.username_id)
    await pcl.get_init_data()
    ...


if __name__ == "__main__":
    run(main())
