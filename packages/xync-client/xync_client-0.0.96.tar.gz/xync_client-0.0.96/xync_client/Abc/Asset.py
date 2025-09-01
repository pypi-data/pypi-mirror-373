from abc import abstractmethod

from xync_schema.models import Agent

from xync_client.Abc.Base import FlatDict, BaseClient

from xync_client.Abc.AuthTrait import BaseAuthTrait


class BaseAssetClient(BaseClient, BaseAuthTrait):
    def __init__(self, agent: Agent):
        self.agent: Agent = agent
        super().__init__(agent.ex, "host")

    # 39: Балансы моих монет
    @abstractmethod
    async def assets(self) -> FlatDict: ...
