from abc import abstractmethod, ABCMeta
from asyncio import get_running_loop
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from playwright.async_api import Page, Playwright
from pyro_client.client.file import FileClient
from xync_client.loader import TOKEN
from xync_schema.enums import UserStatus
from xync_schema.models import PmAgent, User


class LoginFailedException(Exception): ...


class PmAgentClient(metaclass=ABCMeta):
    class Pages(StrEnum):
        base = "https://host"
        LOGIN = base + "login"
        SEND = base + "send"
        OTP_LOGIN = base + "login/otp"

    norm: str
    uid: int
    agent: PmAgent
    bot: FileClient
    page: Page
    pages: type(StrEnum) = Pages
    last_page: int = 0
    last_active: datetime = datetime.now()
    _is_started: bool = False

    async def start(self, pw: Playwright, headed: bool = False) -> "PmAgentClient":
        dct = dict(user__status__gte=UserStatus.PAY, pm__norm=self.norm)
        if self.uid:
            dct.update({"user__username_id": self.uid})

        self.bot = FileClient(TOKEN)
        await self.bot.start()

        self.agent = await PmAgent.get_or_none(**dct).prefetch_related("user__username__session")
        if not self.agent:
            await self.bot.send(f"No active users with agent for {self.norm}!", self.uid)
            raise Exception(f"No active users for {self.norm}!")

        self.browser = await pw.chromium.launch(channel="chrome", headless=not headed)
        context = await self.browser.new_context(storage_state=self.agent.state)
        self.page = await context.new_page()
        await self.page.goto(self.pages.SEND)  # Оптимистично переходим сразу на страницу отправки
        if self.page.url.startswith(self.pages.LOGIN):  # Если перебросило на страницу логина
            await self._login()  # Логинимся
        if not self.page.url.startswith(self.pages.SEND):  # Если в итоге не удалось попасть на отправку
            await self.bot.send(self.norm + " not logged in!", self.uid, photo=await self.page.screenshot())
            raise LoginFailedException(f"User {self.agent.user_id} has not logged in")
        loop = get_running_loop()
        self.last_active = datetime.now()
        loop.create_task(self._idle())  # Бесконечно пасёмся в фоне на странице отправки, что бы куки не протухли
        self._is_started = True
        return self

    async def _idle(self):  # todo: не мешать другим процессам, обновлять на другой вкладке?
        while (await User.get(username_id=self.uid)).status >= UserStatus.ACTIVE:
            await self.page.wait_for_timeout(15 * 1000)
            if self.last_active < datetime.now() - timedelta(seconds=20):
                await self.page.reload()
                self.last_active = datetime.now()
        await self.bot.send(self.norm + " stoped", self.uid)
        await self.stop()

    async def stop(self):
        # save state
        self.agent.state = await self.page.context.storage_state()
        await self.agent.save()
        # closing
        await self.bot.stop()
        await self.page.context.close()
        await self.page.context.browser.close()
        self._is_started = False

    @abstractmethod
    async def _login(self): ...

    @abstractmethod
    async def send(self, dest, amount: int, cur: str) -> tuple[int, bytes, float]: ...

    @abstractmethod  # проверка поступления определенной суммы за последние пол часа (минимум), return точную сумму
    async def check_in(self, amount: int | Decimal | float, cur: str, tid: str | int = None) -> float | None: ...

    @abstractmethod  # видео входа в аккаунт, и переход в историю поступлений за последние сутки (минимум)
    async def proof(self) -> bytes: ...

    def __init__(self, uid: int = None):
        self.uid = uid
