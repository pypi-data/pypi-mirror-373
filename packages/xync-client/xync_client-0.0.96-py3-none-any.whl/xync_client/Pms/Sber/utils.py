import time


async def input_(page, code: str) -> None:
    for i in code:
        await page.keyboard.press(i)
        await page.wait_for_timeout(100)
    time.sleep(3)

async def save_cookies(page, agent):
    cookies = await page.context.storage_state()
    agent.state = cookies
    await agent.save()


async def login_cart(page, number_cart: str, agent) -> None:
    await page.locator('.ORooa1iN_m7TwVK3cepA.j1BVylVDluoRpxKqRP39:has-text("Войти по номеру карты")').click()
    await page.wait_for_selector('input[aria-describedby="cardNumber-description"]', timeout=10000)
    await page.locator('input[aria-describedby="cardNumber-description"]').fill(number_cart)
    await page.locator('button[data-testid="button-continue"]').click()
    await input_(page, input("Введите код из SMS: "))
    passwd = input("Придумайте пороль: ")
    await input_(page,passwd)
    time.sleep(1)
    await input_(page, passwd)
    agent.auth["pass"] = passwd
    await agent.save()
    await save_cookies(page, agent)

async def login_and_password(page, login: str, password: str, agent) -> None:
    await page.locator('.ORooa1iN_m7TwVK3cepA:has-text("По логину")').click()
    await page.locator('input[autocomplete="login"]').fill(login)
    await page.locator('input[name="password"]').fill(password)
    await page.locator('button[data-testid="button-continue"]').click()
    await input_(page, input("Введите код из SMS: "))
    passwd = input("Придумайте пароль: ")
    await input_(page, passwd)
    time.sleep(1)
    await input_(page, passwd)
    agent.auth["pass"] = passwd
    await agent.save()
    await save_cookies(page, agent)


async def logged(page, passcode: str) -> None:
    for i in passcode:
        await page.keyboard.press(i)
        await page.wait_for_timeout(100)