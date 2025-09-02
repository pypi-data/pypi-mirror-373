import asyncio
import time
import os
from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError, Error
from x_model import init_db
from xync_schema import models
from xync_client.loader import TORM



async def send_cred(page, amount):
    await page.goto("https://online.mtsdengi.ru/transfer/card_to_card")
    time.sleep(2)
    await page.click("[name='cardNumberRecipient']")
    await _input(page, "2200700829876027")
    await page.click(".sc-fCLUES.fdwsJd")
    await _input(page, amount)
    await page.click(".sc-CNKsk.jJLXdz.sc-gcfzXs.knNfLR")

async def _input(page, code):
    for i in range(len(code)):
        await page.keyboard.press(code[i])

async def main():
    _ = await init_db(TORM, True)
    agent = await models.PmAgent.filter(pm__norm="mts", auth__isnull=False).first()
    url = "https://online.mtsdengi.ru/"
    storage_state = "state.json" if os.path.exists("state.json") else None
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome",
            headless=False,
            timeout=5000,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-infobars",
                "--disable-extensions",
                "--start-maximized",
            ],
        )
        context = await browser.new_context(storage_state=agent.state)
        page = await context.new_page()
        await page.goto(url)
        if not agent.state:
            await page.locator("#login").fill(agent.auth.get("number"))
            time.sleep(1)
            await page.click(".sc-gKclnd.kaGqJP")
            await _input(page, input("Code: "))
            time.sleep(5)
            cookies = await page.context.storage_state()
            agent.state = cookies
            await agent.save()
        await send_cred(page, "10")
        time.sleep(100)
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
