import asyncio
import time
import os
from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError, Error
from x_model import init_db
from xync_schema import models
from xync_client.loader import TORM


async def send_cred(page):
    await page.goto("https://bank.yandex.ru/pay/payments?modal=%2Ftransfers%3Fproduct%3DWALLET%26direction%3DTRANSFER%26transferType%3DbyPhone%26fromPayment%3Dtrue%26from%3DsuggestedBanks")

async def _input(page, code):
    for i in range(len(code)):
        await page.keyboard.press(code[i])



async def main():
    _ = await init_db(TORM, True)
    agent = await models.PmAgent.filter(pm__norm="yandex", auth__isnull=False).first()
    number = "https://passport.yandex.ru/auth/reg/portal?origin=bank_web&retpath=https%3A%2F%2Fsso.passport.yandex.ru%2Fprepare%3Fuuid%3D33b26edb-0bcd-43e2-b5e0-145d880f043f%26goal%3Dhttps%253A%252F%252Fya.ru%252F%26finish%3Dhttps%253A%252F%252Fbank.yandex.ru%252Fpay%253Fauth%253Dtrue&process_uuid=63e1c65c-54c7-4fc2-b101-a4a2f10032af"
    login = "https://passport.yandex.ru/auth/add/login?retpath=https%3A%2F%2Fbank.yandex.ru%2Fpay%3Fauth%3Dtrue&backpath=https%3A%2F%2Fbank.yandex.ru%2Fpay&origin=bank_web"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=agent.state)
        page = await context.new_page()
        await page.goto(login)
        if not agent.state:
            await page.locator("#passp-field-login").fill(agent.auth.get("login"))
            await page.click(".Button2")
            await _input(page, input("Code: "))
            # await page.locator("#passp-field-phoneCode").fill(input("Code: "))
            time.sleep(2)
            cookies = await page.context.storage_state()
            agent.state = cookies
            await agent.save()
            time.sleep(60)
        else:
            await page.click(".AuthAccountListItem-inner")
            time.sleep(5)
            await _input(page, input("Code: "))
            time.sleep(3)
            await send_cred(page)
            time.sleep(100)
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
