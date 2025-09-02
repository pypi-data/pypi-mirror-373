import pytest

# import uvloop
from abc import abstractmethod
from typing import TypeGuard
from tortoise.backends.asyncpg import AsyncpgDBClient
from x_client.aiohttp import Client as HttpClient
from x_model import init_db
from xync_client.Abc.xtype import DictOfDicts, ListOfDicts, FlatDict, MapOfIdsList
from xync_client.loader import TORM


class BaseTest:
    # loop: AbstractEventLoop
    # @pytest.fixture(scope="session", autouse=True)
    # def event_loop_policy(self):
    #     return uvloop.EventLoopPolicy()
    @pytest.fixture(scope="session", autouse=True)
    async def cn(self) -> AsyncpgDBClient:
        cn: AsyncpgDBClient = await init_db(TORM, True)
        yield cn
        await cn.close()

    @abstractmethod
    @pytest.fixture(scope="session")
    async def clients(self) -> list[HttpClient]: ...

    @staticmethod
    def is_dict_of_dicts(dct: DictOfDicts, not_empty: bool = True) -> TypeGuard[DictOfDicts]:
        if not_empty and not len(dct):
            return False
        return all(isinstance(k, int | str) and isinstance(v, dict) for k, v in dct.items())

    @staticmethod
    def is_dict_of_objects(dct: dict, typ: type, not_empty: bool = True) -> TypeGuard[dict]:  # todo: Generic
        if not_empty and not len(dct):
            return False
        return all(isinstance(k, int | str) and isinstance(v, typ) for k, v in dct.items())

    @staticmethod
    def is_list_of_dicts(lst: ListOfDicts, not_empty: bool = True) -> TypeGuard[ListOfDicts]:
        if not_empty and not len(lst):
            return False
        return all(isinstance(el, dict) for el in lst)

    @staticmethod
    def is_list_of_objects(lst: list, typ: type, not_empty: bool = True) -> TypeGuard[list]:
        if not_empty and not len(lst):
            return False
        return all(isinstance(el, typ) for el in lst)

    @staticmethod
    def is_flat_dict(dct: FlatDict, not_empty: bool = True) -> TypeGuard[FlatDict]:
        if not_empty and not len(dct):
            return False
        return all(isinstance(k, int | str) and isinstance(v, str | int | float) for k, v in dct.items())

    @staticmethod
    def is_map_of_ids(dct: MapOfIdsList, not_empty: bool = True) -> TypeGuard[MapOfIdsList]:
        if not_empty and not len(dct):
            return False
        return all(isinstance(k, int | str) and isinstance(v, list | set) for k, v in dct.items())
