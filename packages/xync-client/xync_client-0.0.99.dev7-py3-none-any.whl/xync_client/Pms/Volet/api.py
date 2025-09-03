import decimal
from asyncio import run, sleep
from datetime import datetime
from hashlib import sha256
from typing import Any

from x_model import init_db
from zeep.client import Client

from xync_client.loader import TORM


class APIClient:
    wsdl = "https://wallet.advcash.com/wsm/merchantWebService?wsdl"

    USD = "USD"
    RUR = "RUR"
    EUR = "EUR"
    GBP = "GBP"
    UAH = "UAH"
    KZT = "KZT"
    BRL = "BRL"
    TRL = "TRL"

    cur_map = {
        "U": "USD",
        "R": "RUB",
        "E": "EUR",
        "G": "GBP",
        "L": "TRY",
        "T": "KZT",
        "V": "VND",
    }

    def __init__(self, api_name: str, api_secret: str, account_email: str):
        self.api_name = api_name
        self.api_secret = api_secret
        self.account_email = account_email
        self.client = Client(self.wsdl)

    def make_auth_token(self) -> str:
        """
        Makes sha256 from API Password:Date UTC in YYYYMMDD format:Time UTC in HH format (only hours, not minutes)
        like Merchant API required
        :return: str
        """
        now_str = datetime.utcnow().strftime("%Y%m%d:%H")
        encoded_string = "{}:{}".format(self.api_secret, now_str).encode("utf8")
        return sha256(encoded_string).hexdigest().upper()

    def make_auth_params(self) -> dict:
        return {
            "apiName": self.api_name,
            "authenticationToken": self.make_auth_token(),
            "accountEmail": self.account_email,
        }

    def make_request(self, action_name: str, params: dict = None):
        action = getattr(self.client.service, action_name)
        if params:
            return action(self.make_auth_params(), params)
        return action(self.make_auth_params())

    def get_balances(self) -> dict[str, tuple[str, decimal]]:
        """
        :return: dict {"account number": amount, ...}
        """
        response = self.make_request("getBalances")
        return {i["id"]: (ct, i["amount"]) for i in response if (ct := self.cur_map.get(i["id"][0]))}

    def send_money(self, to: str, amount: Any, currency: str, note: str = "") -> str:
        """
        :param to: str account number or email
        :param amount: Any with 2 point precisions
        :param currency: str one of available currencies
        :param note: str note for transaction
        :return: str transaction ID
        """
        params = {"amount": amount, "currency": currency, "note": note, "savePaymentTemplate": False}
        if "@" in to:
            params.update(email=to)
        else:
            params.update(walletId=to)
        return self.make_request("sendMoney", params)


period = 5


async def check_payment(cl: APIClient, amount: decimal, cur: str = "RUB", timeout: int = 5 * 60, past: int = 0):
    hist: list = cl.make_request("history", {"transactionDirection": "INCOMING", "count": 3, "from": 0})
    if int(hist[0].amount) == int(amount):
        return hist[0]
    await sleep(period)
    past += period
    if past < timeout:
        return await check_payment(cl, amount, cur, timeout, past)
    return False


async def main():
    _ = await init_db(TORM, True)
    cl = APIClient("main", "mixfixX98", "mixartemev@gmail.com")
    b = cl.get_balances()
    cl.make_request("history", {"transactionDirection": "INCOMING", "count": 100, "from": 0})
    print(b)


if __name__ == "__main__":
    run(main())
