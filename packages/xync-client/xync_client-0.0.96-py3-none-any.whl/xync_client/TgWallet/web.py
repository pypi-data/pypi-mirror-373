import logging

from aiohttp import ClientResponse
from aiohttp.http_exceptions import HttpProcessingError
from x_client.aiohttp import Client
from xync_schema.models import Agent


class Private(Client):
    base_url = "https://walletbot.me"
    middle_url = "/"
    headers = {"Content-Type": "application/json"}
    agent: Agent

    def __init__(self, agent: Agent):
        self.agent = agent
        super().__init__()

    async def _proc(self, resp: ClientResponse, data: dict = None) -> dict | str:
        try:
            return await super()._proc(resp)
        except HttpProcessingError as e:
            if e.code == 401:
                logging.warning("")
                # await self.set_tokens()
                url = resp.url.path.replace(self.middle_url, "", 1)
                res = await self.meth[resp.method](url, data)
                return res

    # Get Status
    async def get_status(self) -> dict:
        status = await self.get("users/public-api/v2/region-verification/status/")
        return status

    # Get Transaction
    async def get_transactions(self, limit: int = 20) -> dict:
        transactions = await self.get("api/v1/transactions/", params={"limit": limit})
        return transactions

    # Get Campaigns
    async def get_campaigns(self) -> dict:
        campaigns = await self.get("v2api/earn/campaigns/")
        return campaigns

    # Get KYC
    async def get_kyc(self) -> dict:
        kyc = await self.post("users/public-api/v2/user/get-kyc")
        return kyc["data"]["userId"]


# async def main():
#     c = Private()
#     await c.get_token()
