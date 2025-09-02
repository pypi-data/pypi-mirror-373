from x_client import Client, repeat_on_fault
from x_client.client import HttpNotFound


class Earn(Client):
    base_url = "https://www.kucoin.com"
    middle_url = "/"

    # 1: Get BETH staking details
    @repeat_on_fault()
    async def get_earn_products(self) -> dict:
        res = await self.get("_pxapi/pool-staking/v3/products/currencies")
        return res["data"]

    # 2: Get ongoing earn products
    @repeat_on_fault()
    async def get_onchain_products(self) -> dict:
        res = await self.get("_api/loan-b2c/outer/condition-currencies")
        return res["data"]

    # 3: Get product detail
    @repeat_on_fault()
    async def get_product_detail(self, pid: int) -> dict:
        try:
            res = await self.get("_pxapi/pool-staking/v3/products/" + str(pid))
        except HttpNotFound:
            return {}
        if not res["success"]:
            pass
        return res["data"] or {}
