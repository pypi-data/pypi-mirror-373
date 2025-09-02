import asyncio
import time
from pydoc import pager

from playwright.async_api import async_playwright, Playwright
import re
from x_model import init_db
from xync_client.loader import TORM
from xync_client.Abc.PmAgent import PmAgentClient
from enum import StrEnum
from decimal import Decimal
from math import ceil
from utils import login_cart, logged, login_and_password



class Client(PmAgentClient):
    class Pages(StrEnum):
        SEND = "https://web7.online.sberbank.ru/main"
        LOGIN = "https://online.sberbank.ru/CSAFront/index.do"
        history = "https://web7.online.sberbank.ru/operations"


    norm: str = "sber"
    pages: type(StrEnum) = Pages



    async def _login(self):
        page = self.page
        await page.goto(self.pages.LOGIN)
        if login := self.agent.auth.get("login"):
            await asyncio.sleep(1)
            if await page.locator('.ORooa1iN_m7TwVK3cepA:has-text("По логину")').is_visible():
                await login_and_password(page, login, self.agent.auth.get("password"), self.agent)
            else:
                await logged(page, self.agent.auth.get("pass"))


    async def send(self, dest: str, amount: float, payment: str, uid: int) -> tuple[int, bytes]:
        page = self.page
        if await page.locator("._1jq69oA3J7l6sIWFSfeXpv:has-text('Повторить вход')").is_visible():
            await self._login()
            print("конец")
        else:
            await page.locator("a#nav-link-payments").click()
            await page.locator(".sxZoARZF").click()
            await page.locator("input#text-field-1").fill(dest)
            await page.locator(".tMUGN6jK").click()
            if len(dest) < 15:
                await page.click('button[title="В другой банк по СБП"]')
                await page.fill("input#text-field-1", payment)
                await page.locator(".Fv3KdbZw").click()
                await page.wait_for_selector("#sbptransfer\\:init\\:summ", state="visible")
                await page.fill("#sbptransfer\\:init\\:summ", str(amount))
                await page.click(".zcSt16vp")
                sms_code = input("Введите код из SMS: ")
                await page.fill('input[autocomplete="one-time-code"]', sms_code)
                await page.click(".zcSt16vp")

            else:
                await page.wait_for_selector("#p2ptransfer\\:xbcard\\:amount", state="visible")
                await page.fill("#p2ptransfer\\:xbcard\\:amount", str(amount))
                await page.wait_for_selector("button.bjm6hnlx", state="visible")
                await page.wait_for_timeout(1000)
                await page.click('button:has-text("Продолжить")')
                await page.click("button.bjm6hnlx")
                await page.click("button.bjm6hnlx")
                sms_code = input("Введите код из SMS: ")
                await page.fill("input.MH9z5OYE", sms_code)
                await page.click("button.bjm6hnlx")

            time.sleep(2)
            async with page.expect_download() as download_info:
                await page.click(".TlmIYvgB")
            download = await download_info.value
            await download.save_as("chek.pdf")
            return 1

    async def check_in(self, amount: float, tid: str | int = None) -> float | None:
        page = self.page
        await page.goto(self.pages.history)
        time.sleep(10)
        amount_and_name = await page.locator(".LPSRZs3v.LMncHFjH").all_text_contents()
        _amount = int(re.sub(r"[^\d]", "", amount_and_name[1]))
        transaction_ = amount_and_name[0].strip().upper() == tid.strip().upper()
        if transaction_:
            if amount <= Decimal(_amount) <= ceil(amount):
                return _amount
            else:
                return None

    async def proof(self) -> bytes:
        context = await self.browser.new_context(
            storage_state=self.agent.state,
            record_video_dir="videos/"
        )
        page = await context.new_page()
        await page.goto(self.pages.history)
        time.sleep(5)
        await context.close()
        video_path = await page.video().path()
        with open(video_path, 'rb') as f:
            video_bytes = f.read()
        return video_bytes


async def main(uid: int):
    _ = await init_db(TORM, True)
    playwright: Playwright = await async_playwright().start()
    sbr = Client(uid)
    await sbr.start(playwright, True)
    await sbr.proof()
    dest, amount, payment = "89308185958", 10 , "Т-Банк"
    tid = await sbr.send(dest, amount, payment, uid)
    # await sbr.check_in(9.5, "Никита Сергеевич Г")
    # file = open("chek.pdf", "rb")
    # await sbr.bot.send_document(uid, BytesIO(file.read()), caption="вот чек", file_name=f"chek_{tid}.pdf")
    await sbr.stop()


if __name__ == "__main__":
    asyncio.run(main(1779829771))
