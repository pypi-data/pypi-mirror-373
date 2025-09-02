from asyncio import run
from playwright.async_api import Playwright, async_playwright

from xync_client.loader import TORM
from xync_client.Pms.Payeer import Client


async def main():
    from x_model import init_db

    _ = await init_db(TORM, True)
    done = set()
    pyr = Client(193017646)
    pw: Playwright = await async_playwright().start()
    await pyr.start(pw, False)
    if r := pyr.check_in(3000, "RUB"):
        am, tid = r
        if tid not in done:
            done.add(tid)

    ...


if __name__ == "__main__":
    run(main())
