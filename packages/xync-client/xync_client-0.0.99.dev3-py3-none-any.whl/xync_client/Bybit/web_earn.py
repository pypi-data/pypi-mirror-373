from enum import IntEnum

from x_client import repeat_on_fault
from x_client.aiohttp import Client
from xync_schema.enums import DepType


class ProductType(IntEnum):
    dual_assets = 2
    flexible_saving_products = 4
    liquidity_mining = 5
    fixed_term_saving_products = 6
    pos_staking_products = 8
    fund_pool = 9


type_map = {
    ProductType.flexible_saving_products: DepType.earn,
    ProductType.fixed_term_saving_products: DepType.earn,
    ProductType.pos_staking_products: DepType.stake,
}


class BybitEarn(Client):  # Bybit async client
    base_url = "https://api2.bybit.com"
    middle_url = "/"

    def __init__(self, token: str = None):
        self.headers = {
            "content-type": "application/json",
            # 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            # 'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            "origin": "https://www.bybit.com",
            "usertoken": token,
        }
        super().__init__()

    """ PUBLIC METHS """

    @repeat_on_fault()
    async def get_coins(self) -> dict:
        res = await self.post("s1/byfi/list-coins")
        return {c["coin_enum"]: c["coin_name"] for c in res["result"]["coins"]}

    @repeat_on_fault()
    async def get_home_earn_products(self, typ: ProductType = ProductType.flexible_saving_products):
        res = await self.post("s1/byfi/get-homepage-product-cards", {"product_type": typ})
        return res["result"]

    @repeat_on_fault()
    async def get_lend_products(self):
        res = await self.post("spot/api/lending/v1/token/list")
        res = [
            {
                "pid": f'{r["token"]}_lend',
                "coin": r["token"],
                "apr": r["apr"],
                "duration": r["period"],
                "min_limit": r["minPurchaseLimit"],
                "max_limit": r["depositLimit"],
                "type": 4,
                "ex_id": 4,
            }
            for r in res["result"]
        ]

    # async def get_earn_products(self):
    #     res = await self.post('s1/byfi/api/v1/get-overview-products')
    #     coins = await self.get_coins()
    #     eps = [{
    #             'coin': await _ccoin(coins[coin]),
    #             'pid': f"{coins[coin]}-{(pt:=ProductType(ep['product_type'])).name}",
    #             'apr': tal[0]['apy_min_e8'] if (tal:=ep['tiered_apy_list']) and tal['apy_min_e8']==tal['apy_min_e8'] else 2,
    #             'type': ProductType(ep['product_type']),
    #             'duration': '',
    #         } for coin, ep in {grp['coin']: grp['product_types'] for grp in res['result']['coin_products']}.items()]
    #     return eps

    @repeat_on_fault()
    async def get_product_detail(self, typ: ProductType = ProductType.pos_staking_products, pid: str = "1"):
        res = await self.post("s1/byfi/get-product-detail", {"product_id": pid, "product_type": typ})
        return res["result"]
