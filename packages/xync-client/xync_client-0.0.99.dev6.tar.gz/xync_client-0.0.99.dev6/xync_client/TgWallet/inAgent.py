from asyncio import run
from re import match
from pyrogram import Client, filters, compose
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from tg_auth import UserStatus
from tortoise.functions import Count
from x_model import init_db

from xync_schema.enums import AssetType
from xync_schema.models import Agent, Order, Ad, Asset, Coin, Fiat, Fiatex, PmEx, PmCur, Cur

from xync_client.TgWallet.pyro import PyroClient
from xync_client.Abc.InAgent import BaseInAgentClient
from xync_client.TgWallet.agent import AgentClient


class InAgentClient(BaseInAgentClient):
    def __init__(self):
        self.pyros: dict[int, PyroClient] = dict()

    async def start(self):
        for agent in await Agent.filter(ex__name="TgWallet", auth__isnone=False).all().prefetch_related("ex", "user"):
            pyro = PyroClient(agent)
            pyro.app.add_handler(MessageHandler(self.got_upd, filters.text & filters.chat("wallet")))
            # app.add_handler(DisconnectHandler(out))
            self.pyros[agent.id] = pyro

        await compose(*[p.app for p in self.pyros.values()])

    async def got_upd(self, c: Client, msg: Message) -> dict:
        pattern = (
            r"^The order OS-[0]?(\d{8,9}) was successfully created on your ad\."
            r" You (buy|sell) (\d+(\.\d+)?) ([A-Z]{2,4}) for (\d+(\.\d+)?) ([A-Z]{2,4})\."
            r"\nPayment method: ([\w\s\-()]+)\n"
        )
        if mtch := match(pattern, msg.text) and (btn := msg.reply_markup.inline_keyboard[0][0]):
            oid, _is_sell, _pm_name = mtch.group(1), mtch.group(2) == "sell", mtch.group(7)
            _ca, _coin, _amount, _cur = mtch.group(3), mtch.group(4), mtch.group(5), mtch.group(6)
            order_id = btn.url.replace("https://t.me/wallet/start?startapp=orderid_", "")
            assert oid == order_id
            cl: AgentClient = self.map[c.name][2]
            await cl.get_order(oid)
            order_db, _ = await Order.update_or_create({}, id=int(oid), taker_id=int(c.name))

    async def order_request_ask(self, oid: int) -> dict:
        pass

    async def request_canceled_notify(self) -> int:
        pass

    async def request_accepted_notify(self) -> int:
        pass

    async def create_orders_forum(self, uid) -> int:
        async with self.app as app:
            app: Client
            forum = await app.create_supergroup(f"xync{uid}", "Xync Orders Group")
            await forum.add_members([uid, "xync_bot", "XyncNetBot"])
            return forum.id


async def main():
    from xync_schema import TORM

    _ = await init_db(TORM, True)
    maker, taker = (
        await Agent.filter(ex__name="TgWallet", auth__isnull=False)
        .prefetch_related("ads", "ex__agents", "user__fiats", "assets__coin")
        .annotate(ads_count=Count("ads"))
        .order_by("-ads_count")
        .limit(2)
        .all()
    )
    maker: Agent
    taker: Agent
    # ex: ExClient = maker.ex.client()
    # coins = await ex.coins()
    mc = maker.client()
    # mp, tp = PyroClient(maker), PyroClient(taker.client())
    massets = await maker.asset_client().assets()
    [
        await Asset.update_or_create(
            {"free": amount}, coin=(await Coin.get_or_create(ticker=coin))[0], agent=maker, typ=AssetType.found
        )
        for coin, amount in massets.items()
    ]
    tassets = await taker.asset_client().assets()
    [
        await Asset.update_or_create(
            {"free": amount}, coin=await Coin.get(ticker=coin), agent=taker, typ=AssetType.found
        )
        for coin, amount in tassets.items()
    ]
    settings = await mc.settings()
    coin_mins = {
        tkr: float(val["minInclusive"])
        for tkr, val in settings["offerSettings"]["offerVolumeLimitsByCurrencyCode"].items()
    }
    if maker_coin := [
        await a.coin
        for a in await maker.assets.all().prefetch_related("coin")
        if coin_mins.get(a.coin.ticker) and a.free >= coin_mins[a.coin.ticker]
    ][0]:
        taker.client()
    elif maker_coin := [
        await a.coin
        for a in await taker.assets.all().prefetch_related("coin")
        if coin_mins.get(a.coin.ticker) and a.free >= coin_mins[a.coin.ticker]
    ][0]:
        maker, taker, _tc = taker, maker, mc
        mc: AgentClient = maker.client()
    else:  # No assets for selling
        raise Exception("No assets for selling")

    for k, f in (await mc.my_fiats()).items():
        fiatex, is_new = Fiatex.get_or_create(ex=maker.ex, exid=k)
        if is_new:
            pmex = await PmEx.get(ex=maker.ex, exid=f["paymentMethod"]["code"]).prefetch_related("pm")
            pmcur = await PmCur.get(pm=pmex.pm, cur=await Cur.get(ticker=f["currency"]))
            await Fiat.create(
                pmcur=pmcur,
                user=maker.user,
            )
        else:
            await fiatex.fiat
        await Fiat.get_or_create(
            {},
        )
    if not maker.ads.related_objects:
        mc.ad_new(
            maker_coin,
        )
    ad = await Ad.filter(
        agent__ex__name="TgWallet", agent__auth__isnull=False, agent__user__status__gte=UserStatus.MEMBER
    ).first()
    pcl = InAgentClient()
    await pcl.start()
    maker = pcl.pyros.pop(ad.agent_id)
    taker = list(pcl.pyros.values())[0]
    await taker.agent.client().order_request(ad.id, ad.minFiat)
    # await pcl.create_orders_forum(agent.user_id)


if __name__ == "__main__":
    run(main())
