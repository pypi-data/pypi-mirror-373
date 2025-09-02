from playwright.async_api import Page, Playwright
from pyro_client.client.bot import BotClient
from pyro_client.client.user import UserClient
from xync_schema.models import User, Gmail

from xync_client.loader import TOKEN


class GmClient:
    uid: int
    user: User
    page: Page
    bot: UserClient = None
    HOME = "https://mail.google.com/mail/u/0/"

    def __init__(self, uid: int):
        self.uid = uid

    async def start(self, pw: Playwright, headed: bool = False):
        self.user = await User.get(username_id=self.uid).prefetch_related("gmail")
        if not self.user.gmail:
            self.user.gmail = await Gmail.create(
                login=input(f"{self.user.last_name} gmail login:"), password=input("password:")
            )
        browser = await pw.chromium.launch(
            channel="chrome",
            headless=not headed,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-infobars",
                "--disable-extensions",
                "--start-maximized",
            ],
        )
        context = await browser.new_context(storage_state=self.user.gmail.auth, locale="en")
        self.page = await context.new_page()
        # go home
        await self.page.goto(self.HOME, timeout=62000)
        if not self.page.url.startswith(self.HOME):
            if await (  # ваще с 0 заходим
                sgn_btn := self.page.locator(
                    'header a[href^="https://accounts.google.com/AccountChooser/signinchooser"]:visible',
                    has_text="sign",
                )
            ).count():
                await sgn_btn.click()
            if self.page.url.startswith("https://accounts.google.com/v3/signin/accountchooser"):  # надо выбрать акк
                await self.page.locator("li").first.click()
            # если предлагает залогиниться
            elif await self.page.locator("h1#headingText", has_text="Sign In").count():
                await self.page.fill("input[type=email]", self.user.gmail.login)
                await self.page.locator("button", has_text="Next").click()
            # осталось ввести пороль:
            await self.page.fill("input[type=password]", self.user.gmail.password)
            await self.page.locator("#passwordNext").click()
            await self.page.wait_for_timeout(3000)
            if self.page.url.startswith("https://accounts.google.com/v3/signin/challenge/dp"):
                await self.load_bot()
                await self.bot.receive("Аппрувни гмейл, у тебя 1.5 минуты", photo=await self.page.screenshot())
        await self.page.wait_for_url(lambda u: u.startswith(self.HOME), timeout=90 * 1000)  # убеждаемся что мы в почте
        self.user.gmail.auth = await self.page.context.storage_state()
        await self.user.gmail.save()

    async def mail_confirm(self):
        lang = await self.page.get_attribute("html", "lang")
        labs = {
            "ru": "Оповещения",
            "en-US": "Updates",
        }
        tab = self.page.get_by_role("heading").get_by_label(labs[lang]).last
        await tab.click()
        rows = self.page.locator("tbody>>nth=4 >> tr")
        row = rows.get_by_text("Volet.com").and_(rows.get_by_text("Please Confirm Withdrawal"))
        if not await row.count():
            await self.bot.receive("А нет запросов от волета", photo=await self.page.screenshot())

        await row.click()
        await self.page.wait_for_load_state()
        btn = self.page.locator('a[href^="https://account.volet.com/verify/"]', has_text="confirm").first
        await btn.click()

    async def load_bot(self):
        if not self.bot:
            bot = await BotClient(TOKEN)
            self.bot = await UserClient(self.uid, bot)
        if not self.bot.is_connected:
            await self.bot.start()

    async def stop(self):
        if self.bot and self.bot.is_connected:  # todo: do not stop if
            await self.bot.stop(False)
        await self.page.context.close()
        await self.page.context.browser.close()


async def _test():
    from x_model import init_db
    from xync_schema import TORM

    _ = await init_db(TORM, True)
    uid = 193017646
    gmc = GmClient(uid)
    try:
        await gmc.start(True)
    except TimeoutError as te:
        raise te
    finally:
        await gmc.stop()


if __name__ == "__main__":
    from asyncio import run

    run(_test())
