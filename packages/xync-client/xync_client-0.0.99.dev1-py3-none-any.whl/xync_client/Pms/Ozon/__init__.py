import time
from asyncio import run, sleep
from x_model import init_db
from xync_schema import models
from xync_client.loader import TORM
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup


async def login(driver, agent) -> None:
    await sleep(2)
    driver.get("https://finance.ozon.ru")
    for cookie in agent.state:
        driver.add_cookie(cookie)
    await sleep(2)
    driver.get("https://finance.ozon.ru/lk")
    await sleep(2)
    if 1:
        pin = agent.auth.get("code")
        actions = ActionChains(driver)
        for char in pin:
            actions.send_keys(char)
        actions.perform()

    if 1:  # todo: проверить что действительно успешно залогинился, и если да, обновить куки:
        agent.state = driver.get_cookies()
        await agent.save()


async def _input(driver, input):
    actions = ActionChains(driver)
    for it in input:
        actions.send_keys(it)
    actions.perform()
    await sleep(1)


async def send_cred(driver, cred, payment, amount):
    driver.get("https://finance.ozon.ru/lk/payments/c2c-transfers?step=SELECT_CONTACT_AND_BANK")
    await sleep(3)
    await _input(driver, cred)
    driver.find_element(By.CLASS_NAME, "contact-item.svelte-1lvu9g8").click()
    # driver.find_element(By.CLASS_NAME, "contact-yourself.svelte-1phpki3").click()
    await sleep(1)
    driver.find_element(By.CLASS_NAME, "item.other-bank.svelte-97i23a.dark").click()
    await sleep(1)
    await _input(driver, payment)
    driver.find_element(By.CLASS_NAME, "item.svelte-97i23a").click()
    await sleep(1)
    driver.find_element(By.CLASS_NAME, "input.svelte-1k6phew").click()
    await _input(driver, amount)
    driver.find_element(By.CLASS_NAME, "submit.svelte-1gsi7c").click()
    await sleep(5)
    driver.find_element(By.CLASS_NAME, "submit.svelte-1gsi7c").click()


async def check_last_transaction(driver, amount, name):
    nm = driver.find_element(By.CLASS_NAME, "purpose.svelte-bgmwdn").text
    at = (
        driver.find_element(By.CLASS_NAME, "money.incoming.svelte-bgmwdn")
        .text.replace(" ", "")
        .replace("₽", "")
        .replace("+", "")
    )
    if nm == name and at == amount:
        print("есть")
    else:
        print("нет")


async def main():
    _ = await init_db(TORM, True)
    agent = await models.PmAgent.filter(pm__norm="ozon", auth__isnull=False).first()
    driver = uc.Chrome(no_sandbox=True)
    driver.implicitly_wait(15)

    try:
        if not agent.state:
            driver.get("https://finance.ozon.ru")
            await sleep(1)
            driver.find_element(By.CLASS_NAME, "content.svelte-404phy").click()
            await sleep(1)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            url = soup.find(title="ozon id")["src"]
            driver.get(url)
            driver.find_element(By.NAME, "autocomplete").send_keys(agent.auth.get("phone"))
            driver.find_element(By.CLASS_NAME, "b25_3_2-a").click()
            await sleep(2)
            if driver.find_element(By.CLASS_NAME, "tsHeadline600Large.c65_3_1-a4").is_displayed():
                driver.find_element(By.CLASS_NAME, "ac2h_47.ga5_3_2-a").click()
            sms_code = input("Введите 6-ти значный код: ")
            driver.find_element(By.CLASS_NAME, "d5_3_2-a.d5_3_2-a5").send_keys(sms_code)
            await sleep(5)
            if 1:  # todo: проверить что действительно успешно залогинился, и если да, обновить куки:
                agent.state = driver.get_cookies()
                await agent.save()

        await login(driver, agent)
        await sleep(2)
        # await send_cred(driver, "+7твой номер", "Сбербанк", "1")
        await check_last_transaction(driver, input("amount:"), input("name:"))
        await sleep(5)

    finally:
        driver.quit()


if __name__ == "__main__":
    run(main())
