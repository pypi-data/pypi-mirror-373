import asyncio
import time
from playwright.async_api import async_playwright, Playwright
from xync_client.loader import TORM
from xync_client.Abc.PmAgent import PmAgentClient
from enum import StrEnum
import io
import urllib.request
from decimal import Decimal
from math import ceil


async def _input(page, code):
    for i in range(len(code)):
        await page.keyboard.press(code[i])


async def login(page, agent):
    await page.wait_for_timeout(200)
    await page.locator('[automation-id="phone-input"]').fill(agent.auth.get("number"))
    await page.locator('[automation-id="button-submit"] svg').click()
    await page.locator('[automation-id="otp-input"]').fill(input("Введите код: "))
    time.sleep(3)
    await page.locator('[automation-id="cancel-button"]', has_text="Не сейчас").click(delay=500)
    time.sleep(5)


class Client(PmAgentClient):
    class Pages(StrEnum):
        LOGIN = "https://www.tbank.ru/auth/login/"
        SEND = "https://www.tbank.ru/mybank/"
        SEND_CARD = "https://www.tbank.ru/mybank/payments/transfer-card-to-card/?internal_source=homePayments_transferList_category"
        HISTORY = "https://www.tbank.ru/events/feed"

    norm: str = "tinkoff"
    pages: type(StrEnum) = Pages

    async def send(self, cred, amount, payment, email: str | None = None):
        page = self.page
        if len(cred) < 15:
            # Переходим на сбп и вводим данные получателя
            await page.locator(
                '[data-qa-type="desktop-ib-pay-buttons"] [data-qa-type="atomPanel pay-card-0"]',
                has_text="Перевести по телефону",
            ).click()
            await page.locator('[data-qa-type="recipient-input.value.placeholder"]').click()
            await page.wait_for_timeout(300)
            await page.locator('[data-qa-type="recipient-input.value.input"]').fill(cred)
            await page.locator('[data-qa-type="amount-from.placeholder"]').click()
            await page.locator('[data-qa-type="amount-from.input"]').fill(amount)
            await page.wait_for_timeout(300)
            await page.locator('[data-qa-type="bank-plate-other-bank click-area"]').click()
            await page.locator('[data-qa-type*="inputAutocomplete.value.input"]').click()
            await page.locator('[data-qa-type*="inputAutocomplete.value.input"]').fill(payment)
            await page.wait_for_timeout(300)
            await page.locator('[data-qa-type="banks-popup-list"]').click()
            await page.locator('[data-qa-type="transfer-button"]').click()
        else:
            # карта
            await page.goto(self.pages.SEND_CARD)
            time.sleep(2)
            await page.locator(".cbQxXyBQr").nth(1).click()
            await _input(page, cred)
            await page.locator(".cbQxXyBQr").nth(2).click()
            await _input(page, amount)
            await page.locator('button[data-qa-type="submit-button"][type="submit"]').click()
            if not email:
                href = await page.locator(
                    'a[data-qa-type="click-area desktop-fry-actions-success-payment.receipt"]'
                ).get_attribute("href")
                return href
            else:
                await page.locator(".ebAIjfBEB:has-text('Отправить на почту')").click()
                await page.locator(".sb0--rz3uQ").click()
                await page.locator("[inputmode='email']").fill(email)
                await page.locator(".bbiH7oQgN").click()

    async def _login(self):
        page = self.page
        await login(page, self.agent)
        cookies = await page.context.storage_state()
        self.agent.state = cookies
        await self.agent.save()

    async def check_in(self, amount: float, tid: str | int = None) -> float | None:
        page = self.page
        try:
            await page.goto(self.pages.HISTORY)
        except Exception:
            await page.wait_for_timeout(1000)
            await page.goto(self.pages.HISTORY)
            amount_ = await page.locator(".ab72ydp1G.abR9YYQVn").first.text_content()
            am = amount_.replace(" ₽", "").replace("−", "")
            transaction = (
                await page.locator("[data-qa-type='atom-operations-feed-operation-title']").nth(0).text_content()
            )
            if transaction == tid:
                if amount <= Decimal(am) <= ceil(amount):
                    return am
                else:
                    return None


async def proof(self) -> bytes:
    context = await self.browser.new_context(storage_state=self.agent.state, record_video_dir="videos/")
    page = await context.new_page()
    await page.goto(self.pages.HISTORY)
    await page.mouse.wheel(0, 400)
    time.sleep(5)
    await context.close()
    video_path = await page.video().path()
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    return video_bytes


async def main(uid):
    from x_model import init_db

    _ = await init_db(TORM, True)
    playwright: Playwright = await async_playwright().start()
    t = Client(uid)
    await t.start(playwright, True)
    check_url = await t.send("9308185958", "10", "Сбербанк", "nikitagaldikas869@gmail.com")
    if check_url:
        await t.bot.send_document(
            uid, io.BytesIO(urllib.request.urlopen(check_url).read()), caption="вот чек", file_name="chek_1.pdf"
        )
    await t.proof()
    await t.check_in(10)
    await t.stop()


if __name__ == "__main__":
    asyncio.run(main(1779829771))
