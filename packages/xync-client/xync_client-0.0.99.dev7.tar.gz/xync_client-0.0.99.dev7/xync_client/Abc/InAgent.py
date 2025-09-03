from abc import abstractmethod

from pyro_client.client.file import FileClient
from xync_client.Abc.PmAgent import PmAgentClient
from xync_schema.models import Actor

from xync_client.Abc.Agent import BaseAgentClient


class BaseInAgentClient:
    pmacs: dict[int, PmAgentClient] = {}

    def __init__(self, actor: Actor, bot: FileClient):
        self.agent_client: BaseAgentClient = actor.client(bot)

    @abstractmethod
    async def start_listen(self) -> bool: ...

    # 3N: [T] - Уведомление об одобрении запроса на сделку
    @abstractmethod
    async def request_accepted_notify(self) -> int: ...  # id
