import logging

import pytest
from xync_client.Abc.Asset import BaseAssetClient

from xync_client.Abc.BaseTest import BaseTest
from xync_schema.enums import ExStatus, ExAction
from xync_schema.models import Ex, ExStat as ExTest

from xync_client.Abc.Base import FlatDict


@pytest.mark.asyncio(loop_scope="session")
class TestAsset(BaseTest):
    @pytest.fixture(scope="class", autouse=True)
    async def clients(self) -> list[BaseAssetClient]:
        exs = (
            await Ex.filter(status__gt=ExStatus.plan, agents__auth__isnull=False)
            .distinct()
            .prefetch_related("agents__ex")
        )
        agents = [[ag for ag in ex.agents if ag.auth][0] for ex in exs]
        clients: list[BaseAssetClient] = [agent.asset_client() for agent in agents]
        yield clients
        [await client.close() for client in clients]

    # 39
    async def test_assets(self, clients: list[BaseAssetClient]):
        for client in clients:
            assets: FlatDict = await client.assets()
            ok = self.is_flat_dict(assets)
            t, _ = await ExTest.update_or_create({"ok": ok}, ex=client.agent.ex, action=ExAction.assets)
            assert t.ok, "No curs"
            logging.info(f"{client.agent.ex.name}:{ExAction.assets.name} - ok")
