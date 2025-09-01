from binance import AsyncClient


class Ebac(AsyncClient):  # Earn Binance async client
    HOST = 'https://api-gcp.binance.com/sapi/v1/simple-earn/'

    async def _req(self, url: str, params: dict = None, is_post: bool = True) -> dict:
        return await self._request('post' if is_post else 'get', self.HOST+url, True, data=params or {})

    async def _get_pub(self, url: str, params: dict = None) -> dict:
        return await self._request('get', url, False, data=params or {})

    async def flex_products(self, page: int = 1, asset: str = None) -> []:
        res = await self._req('flexible/list', {'current': page, 'size': 100, 'asset': asset}, False)
        for i in range(res['total'] // 100):
            res['rows'] += (await self._req('flexible/list', {'current': i+2, 'size': 100, 'asset': asset}, False))['rows']
        return res['rows']

    async def lock_products(self, page: int = 1, asset: str = None) -> []:
        res = await self._req('locked/list', {'current': page, 'size': 100, 'asset': asset}, False)
        for i in range(res['total'] // 100):
            res['rows'] += (await self._req('locked/list', {'current': i+2, 'size': 100, 'asset': asset}, False))['rows']
        return res['rows']

    async def buy_flex_product(self, product_id: str, amount: float) -> dict:
        return await self._req('flexible/subscribe', {'productId': product_id, 'amount': amount, 'autoSubscribe': True})

    async def buy_lock_product(self, product_id: str, amount: float) -> dict:
        return await self._req('locked/subscribe', {'productId': product_id, 'amount': amount, 'autoSubscribe': True})

    async def redeem_lock_product(self, position_id: int) -> dict:
        return await self._req('locked/redeem', {'positionId': position_id})

    async def redeem_flex_product(self, position_id: int, amount: float = None) -> dict:
        params = {'positionId': position_id, **({'amount': amount} if amount else {'redeemAll': True})}
        return await self._req('flexible/redeem', params)

    async def flex_position(self, product_id: str = None) -> []:
        res = await self._req('flexible/position', {'productId': product_id, 'size': 100}, False)
        return res['rows']

    async def lock_position(self, position_id: int = None, project_id: str = None, page: int = 1) -> []:
        res = await self._req('locked/position', {'positionId': position_id, 'projectId': project_id, 'size': 100, 'current': page}, False)
        return res['rows']

    async def account(self) -> dict:
        return await self._req('account', is_post=False)

    async def flex_buy_history(self, product_id: str, purchase_id: int = None, asset: str = None) -> []:
        res = await self._req('flexible/history/subscriptionRecord', {
            'productId': product_id, 'purchaseId': purchase_id, 'asset': asset, 'size': 100
        }, False)
        return res['rows']

    async def lock_buy_history(self, purchase_id: int = None, asset: str = None) -> []:
        res = await self._req('locked/history/subscriptionRecord', {
            'purchaseId': purchase_id, 'asset': asset, 'size': 100
        }, False)
        return res['rows']

    async def flex_redeem_history(self, product_id: str, redeem_id: int = None, asset: str = None) -> []:
        res = await self._req('flexible/history/subscriptionRecord', {
            'productId': product_id, 'redeemId': redeem_id, 'asset': asset, 'size': 100
        }, False)
        return res['rows']

    async def lock_redeem_history(self, position_id: int, redeem_id: int = None, asset: str = None) -> []:
        res = await self._req('locked/history/subscriptionRecord', {
            'positionId': position_id, 'redeemId': redeem_id, 'asset': asset, 'size': 100
        }, False)
        return res['rows']

    async def flex_quota(self, product_id: str) -> float:
        res = await self._req('locked/personalLeftQuota', {'productId': product_id}, False)
        return float(res['leftPersonalQuota'])

    async def lock_quota(self, product_id: str) -> float:
        res = await self._req('locked/personalLeftQuota', {'productId': product_id}, False)
        return float(res['leftPersonalQuota'])

    async def get_beth_rate(self) -> float:
        res = await self._get_pub('https://www.binance.com/bapi/earn/v1/public/pos/cftoken/project/getPurchasableProject')
        return float(res['data']['annualInterestRate'])
