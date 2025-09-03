from xync_client.Abc.Base import FlatDict
from xync_client.Abc.Asset import BaseAssetClient
from xync_client.TgWallet.auth import AuthClient


class AssetClient(BaseAssetClient, AuthClient):
    # 39: Балансы моих монет
    async def assets(self) -> FlatDict:
        asss = await self._get("/api/v1/accounts/")
        ass = {ass["currency"]: ass["available_balance"] for ass in asss["accounts"]}
        return ass
