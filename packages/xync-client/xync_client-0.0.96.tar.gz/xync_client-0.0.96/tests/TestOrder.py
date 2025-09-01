import pytest

from xync_client.Abc.Base import BaseClient
from xync_client.AbcTest.BaseTest import BaseTest


class AgentTest(BaseTest):
    @pytest.fixture(scope="class")
    async def cl(self) -> BaseClient:
        agent = (await self.exq).agents.filter(auth__not_isnull=True).first()
        acl = BaseClient(agent)
        yield acl
        await acl.close()

    @pytest.fixture(scope="class")
    async def cl1(self) -> BaseClient:
        agent = (await self.exq).agents.filter(auth__not_isnull=True).offset(1).first()
        acl = BaseClient(agent)
        yield acl
        await acl.close()
