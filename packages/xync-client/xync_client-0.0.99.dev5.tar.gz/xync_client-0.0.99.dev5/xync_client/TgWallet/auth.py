from x_auth.models import Session
from x_client.http import Client as HttpClient
from xync_schema.models import Actor

from xync_client.Abc.Auth import BaseAuthClient
from xync_client.TgWallet.pyro import WalletAuthClient


class AuthClient(BaseAuthClient):
    tg_session: Session = None

    async def _get_auth_hdrs(self) -> dict[str, str]:
        if not self.tg_session:
            self.tg_session = await Session.filter(user__user__person__actors__ex=self.ex).order_by("-date").first()
        pyro = WalletAuthClient(self.tg_session.user_id)
        if not pyro.is_connected:
            await pyro.start()
        init_data = await pyro.get_init_data()
        tokens = HttpClient("walletbot.me")._post("/api/v1/users/auth/", init_data)
        # todo: refact actor.exid actualize
        if not self.actor:
            self.actor = await Actor.get(ex=self.ex, person__user__username_id=self.tg_session.user_id)
        if self.actor.exid != tokens["user_id"]:
            self.actor.exid = tokens["user_id"]
            await self.actor.save()
        # end: actor.exid actualize
        pref = "" if self.__class__.__name__ == "AssetClient" else "Bearer "  # todo: dirty hack
        return {"Authorization": pref + tokens["jwt"]}  # "Wallet-Authorization": tokens["jwt"],
