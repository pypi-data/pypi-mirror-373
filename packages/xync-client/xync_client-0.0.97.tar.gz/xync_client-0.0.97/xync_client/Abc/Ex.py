import logging
from abc import abstractmethod
from asyncio import sleep

from aiohttp import ClientSession, ClientResponse
from msgspec import Struct
from pyro_client.client.file import FileClient
from tortoise.exceptions import MultipleObjectsReturned, IntegrityError
from x_client.aiohttp import Client as HttpClient
from xync_schema import models
from xync_schema.enums import FileType
from xync_schema.xtype import CurEx, CoinEx, BaseAd, BaseAdIn

from xync_client.Abc.xtype import PmEx, MapOfIdsList
from xync_client.pm_unifier import PmUnifier, PmUni


class BaseExClient(HttpClient):
    cur_map: dict[int, str] = {}
    unifier_class: type = PmUnifier
    logo_pre_url: str
    bot: FileClient
    ex: models.Ex

    def __init__(
        self,
        ex: models.Ex,
        bot: FileClient,
        attr: str = "host_p2p",
        headers: dict[str, str] = None,
        cookies: dict[str, str] = None,
        proxy: models.Proxy = None,
    ):
        self.ex = ex
        self.bot = bot
        super().__init__(getattr(ex, attr), headers, cookies, proxy and proxy.str())

    @abstractmethod
    def pm_type_map(self, typ: models.PmEx) -> str: ...

    # 19: Список поддерживаемых валют тейкера
    @abstractmethod
    async def curs(self) -> dict[str, CurEx]:  # {cur.ticker: cur}
        ...

    # 20: Список платежных методов
    @abstractmethod
    async def pms(self, cur: models.Cur = None) -> dict[int | str, PmEx]:  # {pm.exid: pm}
        ...

    # 21: Список платежных методов по каждой валюте
    @abstractmethod
    async def cur_pms_map(self) -> MapOfIdsList:  # {cur.exid: [pm.exid]}
        ...

    # 22: Список торгуемых монет (с ограничениям по валютам, если есть)
    @abstractmethod
    async def coins(self) -> dict[str, CoinEx]:  # {coin.ticker: coin}
        ...

    # 23: Список пар валюта/монет
    @abstractmethod
    async def pairs(self) -> tuple[MapOfIdsList, MapOfIdsList]: ...

    # 24: Список объяв по (buy/sell, cur, coin, pm)
    @abstractmethod
    async def ads(
        self,
        coin_exid: str,
        cur_exid: str,
        is_sell: bool,
        pm_exids: list[str | int] = None,
        amount: int = None,
        lim: int = None,
    ) -> list[BaseAd]:  # {ad.id: ad}
        ...

    # 42: Чужая объява по id
    @abstractmethod
    async def ad(self, ad_id: int) -> BaseAd: ...

    # Преобразрование объекта объявления из формата биржи в формат xync
    @abstractmethod
    async def ad_epyd2pydin(self, ad: BaseAd) -> BaseAdIn: ...  # my_uid: for MyAd

    # 99: Страны
    async def countries(self) -> list[Struct]:
        return []

    # Импорт валют Cur-ов (с CurEx-ами)
    async def set_curs(self, cookies: dict = None) -> bool:
        # Curs
        cur_pyds: dict[str, CurEx] = await self.curs()
        curs: dict[int | str, models.Cur] = {
            exid: (await models.Cur.update_or_create({"rate": cur_pyd.rate or 0}, ticker=cur_pyd.ticker))[0]
            for exid, cur_pyd in cur_pyds.items()
        }
        curexs = [
            models.CurEx(**c.model_dump(exclude_none=True), cur=curs[c.exid], ex=self.ex) for c in cur_pyds.values()
        ]
        # CurEx
        await models.CurEx.bulk_create(curexs, update_fields=["minimum", "scale"], on_conflict=["cur_id", "ex_id"])

    # Импорт Pm-ов (с PmCur-, PmEx- и Pmcurex-ами) и валют (с CurEx-ами) с биржи в бд
    async def set_pms(self, cookies: dict = None) -> bool:
        if cookies:
            self.session.cookie_jar.update_cookies(cookies)
        curs: dict[int | str, models.Cur] = {
            exid: (await models.Cur.update_or_create({"rate": cur_pyd.rate or 0}, ticker=cur_pyd.ticker))[0]
            for exid, cur_pyd in (await self.curs()).items()
        }
        # Pms
        pmexs_epyds: dict[int | str, PmEx] = {
            k: v for k, v in sorted((await self.pms()).items(), key=lambda x: x[1].name) if v.name
        }  # sort by name
        pms: dict[int | str, models.Pm] = dict({})
        prev = 0, "", "", None  # id, normd-name, orig-name
        cntrs: list[tuple[str, str]] = [
            (n.lower(), s and s.lower()) for n, s in await models.Country.all().values_list("name", "short")
        ]
        common_reps = await models.PmRep.filter(ex_id__isnull=True)
        reps = self.ex.pm_reps.related_objects
        uni = self.unifier_class(cntrs, reps + common_reps)
        for k, pmex in pmexs_epyds.items():
            pmu: PmUni = uni(pmex.name)
            country_id = (
                await models.Country.get(name__iexact=cnt).values_list("id", flat=True)
                if (cnt := pmu.country)
                else None
            )
            if prev[2] == pmex.name and pmu.country == prev[3]:  # оригинальное имя не уникально на этой бирже
                logging.warning(f"Pm: '{pmex.name}' duplicated with ids {prev[0]}: {k} on {self.ex.name}")
                # новый Pm не добавляем, а берем старый с этим названием
                pm_ = pms.get(prev[0], await models.Pm.get_or_none(norm=prev[1], country_id=country_id))
                # и добавляем PmEx для него
                await models.PmEx.update_or_create({"name": pmex.name}, ex=self.ex, exid=k, pm=pm_)
            elif (
                prev[1] == pmu.norm and pmu.country == prev[3]
            ):  # 2 разных оригинальных имени на этой бирже совпали при нормализации
                logging.error(
                    f"Pm: {pmex.name}&{prev[2]} overnormd as {pmu.norm} with ids {prev[0]}: {k} on {self.ex.name}"
                )
                # новый Pm не добавляем, только PmEx для него
                # новый Pm не добавляем, а берем старый с этим названием
                pm_ = pms.get(prev[0], await models.Pm.get_or_none(norm=prev[1], country_id=country_id))
                # и добавляем.обновляем PmEx для него
                await models.PmEx.update_or_create({"pm": pm_}, ex=self.ex, exid=k, name=pmex.name)
            else:
                pmin = models.Pm.validate({**pmu.model_dump(), "country_id": country_id, "typ": pmex.typ})
                try:
                    pms[k], _ = await models.Pm.update_or_create(**pmin.df_unq())
                except (MultipleObjectsReturned, IntegrityError) as e:
                    raise e
            prev = k, pmu.norm, pmex.name, pmu.country
        await models.PmCur.update_or_create(  # todo: NA HU YA???
            cur=await models.Cur.get(ticker="THB"), pm=await models.Pm.get(norm="cash in person")
        )

        # Pmexs
        async with ClientSession(headers=getattr(self, "logo_headers", None)) as ss:
            pmexs = [
                models.PmEx(
                    # todo: refact logo
                    exid=k,
                    ex=self.ex,
                    pm=pm,
                    name=pmexs_epyds[k].name,
                    logo=await self.logo_save(pmexs_epyds[k].logo, ss),
                )
                for k, pm in pms.items()
            ]

        await models.PmEx.bulk_create(pmexs, on_conflict=["ex_id", "exid"], update_fields=["pm_id", "logo_id", "name"])
        # PmEx banks
        for k, pmex in pmexs_epyds.items():
            if banks := pmex.banks:
                pmex = await models.PmEx.get(ex=self.ex, exid=k)  # pm=pms[k],
                for b in banks:
                    await models.PmExBank.update_or_create({"name": b.name}, exid=b.exid, pmex=pmex)

        cur2pms = await self.cur_pms_map()
        # # Link PayMethods with currencies
        pmcurs = set()
        for cur_id, exids in cur2pms.items():
            for exid in exids:
                if not (pm_id := pms.get(exid) and pms[exid].id):
                    if pmex := await models.PmEx.get_or_none(ex=self.ex, exid=exid):
                        pm_id = pmex.pm_id
                    else:
                        logging.critical(f"For cur {cur_id} not found pm#{exid}")
                        continue
                if cur_db := curs.get(cur_id):
                    pmcurs.add((await models.PmCur.update_or_create(cur=cur_db, pm_id=pm_id))[0])
        # pmcurexs = [Pmcurex(pmcur=pmcur, ex=self.ex) for pmcur in pmcurs]
        # await Pmcurex.bulk_create(pmcurexs)
        return True

    async def logo_save(self, url: str | None, ss: ClientSession) -> models.File | None:
        if url or (file := None):
            if not url.startswith("https:"):
                if not url.startswith("/"):
                    url = "/" + url
                url = "https://" + self.logo_pre_url + url
            return await self.file_upsert(url, ss)
        return file

    # Импорт монет (с CoinEx-ами) с биржи в бд
    async def set_coins(self):
        coinexs: dict[str, CoinEx] = await self.coins()
        coins_db: dict[int, models.Coin] = {
            c.exid: (
                await models.Coin.update_or_create({"scale": c.scale} if c.scale is not None else {}, ticker=c.ticker)
            )[0]
            for c in coinexs.values()
        }
        coinexs_db: list[models.CoinEx] = [
            models.CoinEx(
                scale=(scl := c.scale or self.coin_scales[c.ticker]),
                coin=coins_db[c.exid],
                ex=self.ex,
                exid=c.exid,
                minimum=c.minimum and c.minimum * 10**scl,
            )
            for c in coinexs.values()
        ]
        await models.CoinEx.bulk_create(coinexs_db, update_fields=["minimum"], on_conflict=["coin_id", "ex_id"])
        return True

    # Импорт пар биржи в бд
    async def set_pairs(self):
        curs: dict[str, CurEx] = {
            k: (await models.Cur.get_or_create(ticker=c.ticker))[0] for k, c in (await self.curs()).items()
        }
        coins: dict[str, CoinEx] = {
            k: (await models.Coin.get_or_create(ticker=c.ticker))[0] for k, c in (await self.coins()).items()
        }
        prs: tuple[dict, dict] = await self.pairs()
        for is_sell in (0, 1):
            pss: list[models.PairSide] = []
            for cur, coinz in prs[is_sell].items():
                for coin in coinz:
                    pair, _ = await models.Pair.get_or_create(coin=coins[coin], cur=curs[cur])
                    # pairex, _ = await models.PairEx.get_or_create(pair=pair, ex=self.ex)  # todo: разные ли комишки на покупку и продажу?
                    pss += [models.PairSide(is_sell=is_sell, pair=pair)]
            await models.PairSide.bulk_create(pss, ignore_conflicts=True)
        return True

    # Сохранение чужого объявления (с Pm-ами) в бд
    async def ad_pydin2db(self, ad_pydin: BaseAdIn) -> models.Ad:
        dct = ad_pydin.model_dump()
        dct["exid"] = dct.pop("id")
        ad_in = models.Ad.validate(dct)
        ad_db, _ = await models.Ad.update_or_create(**ad_in.df_unq())
        await ad_db.credexs.add(*getattr(ad_pydin, "credexs_", []))
        await ad_db.pmexs.add(*getattr(ad_pydin, "pmexs_", []))
        return ad_db

    async def file_upsert(self, url: str, ss: ClientSession = None) -> models.File:
        if not (file := await models.File.get_or_none(name__startswith=url.split("?")[0])):
            ss = ss or self.session
            if (resp := await ss.get(url)).ok:
                byts = await resp.read()
                upf, ref = await self.bot.save_doc(byts, resp.content_type)
                await sleep(0.3)
                typ = FileType[resp.content_type.split("/")[-1]]
                file, _ = await models.File.update_or_create({"ref": ref, "size": len(byts), "typ": typ}, name=url)
                # fr = await pbot.get_file(file.ref)  # check
        return file

    async def _proc(self, resp: ClientResponse, data_key: str = None, bp: dict | str = None) -> dict | str:
        if resp.status in (403,):
            proxy = await models.Proxy.filter(valid=True, country__short__not="US").order_by("-updated_at").first()
            cookies = self.session.cookie_jar.filter_cookies(self.session._base_url)
            self.session = ClientSession(
                self.session._base_url, headers=self.session.headers, cookies=cookies or None, proxy=proxy.str()
            )
            return await self.METHS[resp.method](self, resp.url.path, bp, data_key=data_key)
        return await super()._proc(resp, data_key, bp)
