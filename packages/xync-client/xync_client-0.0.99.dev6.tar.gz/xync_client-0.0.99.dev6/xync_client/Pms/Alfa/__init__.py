import asyncio

from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError


async def main():
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
        context = await browser.new_context(storage_state="state.json")
        page = await context.new_page()
        await page.goto("https://web.alfabank.ru/dashboard")
        await page.wait_for_timeout(1000)
        try:
            await page.wait_for_url("https://web.alfabank.ru/dashboard")
            await page.wait_for_timeout(1000)
        # Новый пользователь
        except TimeoutError:
            if page.wait_for_url(
                "https://private.auth.alfabank.ru/passport/cerberus-mini-blue/dashboard-blue/phone_auth/"
            ):
                await page.locator('[data-test-id="phoneInput-form-control-inner"] [data-test-id="phoneInput"]').fill(
                    "79680250007"
                )
                await page.wait_for_timeout(1000)
                await page.locator("span", has_text="Вперёд").click(delay=500)
                await page.locator('[data-test-id="card-account-input"]').fill("2200150631057988")
                await page.locator('[data-test-id="card-account-continue-button"]').click()
                await page.locator(
                    '[class*=confirmation__component] [class*=code-input] [autocomplete="one-time-code"]'
                ).fill(input("Введите код"))
                await page.wait_for_timeout(1000)
                if await page.locator('[data-test-id="trust-device-page-cancel-btn"]').is_visible():
                    await page.wait_for_timeout(500)
                    await page.locator('[data-test-id="trust-device-page-submit-btn"]').click()
                    if page.locator('[data-test-id="new-password"]'):
                        await page.locator('[data-test-id="new-password"]').click()
                        await page.locator('[data-test-id="new-password"]').fill("1469")
                        await page.locator('[data-test-id="new-password-again"]').click()
                        await page.locator('[data-test-id="new-password-again"]').fill("1469")
                        await page.locator('[data-test-id="submit-button"]').click()
                await page.context.storage_state(path="state.json")
            else:
                pass

        # Переходим на сбп и вводим данные получателя
        await page.wait_for_timeout(300)
        await page.locator('[data-test-id="item"]', has_text="Платежи").click()
        await page.locator('[data-test-id="transfer-item"]', has_text="По номеру телефона").click()
        await page.wait_for_timeout(300)
        await page.locator('[data-test-id="phone-intl-input"]').fill("79992259898")
        await page.locator('[data-test-id="recipient-select-option"]', has_text="Озон Банк").click()
        await page.locator('[data-test-id="money-input"]').fill("100")
        await page.wait_for_timeout(300)
        await page.locator("button", has_text="Продолжить").click()
        await page.locator('[data-test-id="transfer-by-phone-confirmation-submit-btn"]').click()
        await page.locator('[autocomplete="one-time-code"]').fill(input("Введите код"))
        await page.locator('[data-test-id="ready-button"]').click()

        # Проверка последнего платежа
        await page.wait_for_timeout(500)
        if page.locator('[data-test-id="pincode-title"]') and not page.wait_for_url(
            "https://web.alfabank.ru/dashboard"
        ):
            await page.wait_for_timeout(500)
            await page.locator('[type="password"]').fill("2508")
            await page.locator("span", has_text="Вперёд").click()
        await page.wait_for_timeout(1000)
        await page.locator('[data-test-id="item"] [href="/history/"]', has_text="История").click()
        await page.wait_for_timeout(1000)
        transactions_loc = page.eval_on_selector_all(
            '[data-test-id="transaction-status"]',
            """elements => elements.map(el => el.querySelector('span')?.textContent?.trim()).filter(Boolean)""",
        )
        transactions = await transactions_loc
        result = recursion_payments(500, transactions)
        if result == 500:
            print("Платеж", result, "получен")
        else:
            print("Ничегошеньки нет")
        await context.close()
        # await page.video.path()
        ...
    await browser.close()


def recursion_payments(amount: int, transactions: list):
    tran = transactions.pop(0)
    normalized_tran = tran.split(",")[0]
    if int(normalized_tran) != amount:
        return recursion_payments(amount, transactions)
    return int(float(normalized_tran))


asyncio.run(main())
