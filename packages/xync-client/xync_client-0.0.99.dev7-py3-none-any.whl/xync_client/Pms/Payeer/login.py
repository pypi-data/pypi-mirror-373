from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from xync_schema.models import PmAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


async def login(agent: PmAgent):
    driver = uc.Chrome(no_sandbox=True)
    wait = WebDriverWait(driver, timeout=10)
    try:
        driver.get("https://payeer.com/ru/auth")
        wait.until(EC.invisibility_of_element_located((By.TAG_NAME, "lottie-player")))
        login_link = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "button.button_empty")))
        try:
            login_link.click()
        except Exception:
            driver.execute_script("arguments[0].click();", login_link)
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.send_keys(agent.auth.get("email"))
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys(agent.auth.get("password"))
        login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login-form__login-btn.step1")))
        try:
            login_button.click()
        except Exception:
            driver.execute_script("arguments[0].click();", login_button)
        try:
            login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login-form__login-btn.step1")))
            driver.execute_script("arguments[0].click();", login_button)
        except Exception:
            pass
        if (v := driver.find_elements(By.CLASS_NAME, "form-input-top")) and v[0].text == "Введите проверочный код":
            code = input("Email code: ")
            actions = ActionChains(driver)
            for char in code:
                actions.send_keys(char).perform()
            step2_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login-form__login-btn.step2")))
            try:
                step2_button.click()
            except Exception:
                driver.execute_script("arguments[0].click();", step2_button)
    finally:
        driver.quit()
