from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Literal, Union, overload
from ...config import MongoDBDatabaseConfig
from ...enums import Connection


class MongoDBClientManager:
    def __init__(self, config: MongoDBDatabaseConfig) -> None:
        self.config = config
        self._async_client: AsyncIOMotorClient = self._init(Connection.ASYNC)
        self._sync_client: MongoClient = self._init(Connection.SYNC)

    @overload
    def _init(self, connection: Literal[Connection.ASYNC]) -> AsyncIOMotorClient: ...
    @overload
    def _init(self, connection: Literal[Connection.SYNC]) -> MongoClient: ...
    def _init(
        self, connection: Connection = Connection.ASYNC
    ) -> Union[AsyncIOMotorClient, MongoClient]:
        url = self.config.connection.make_url(connection)

        pooling_kwargs = self.config.pooling.model_dump(
            by_alias=True, exclude_none=True
        )

        if connection is Connection.ASYNC:
            self._async_client = AsyncIOMotorClient(url, **pooling_kwargs)
            return self._async_client
        else:
            self._sync_client = MongoClient(url, **pooling_kwargs)
            return self._sync_client

    @overload
    def get(self, connection: Literal[Connection.ASYNC]) -> AsyncIOMotorClient: ...
    @overload
    def get(self, connection: Literal[Connection.SYNC]) -> MongoClient: ...
    def get(
        self, connection: Connection = Connection.ASYNC
    ) -> Union[AsyncIOMotorClient, MongoClient]:
        if connection is Connection.ASYNC:
            return self._async_client
        elif connection is Connection.SYNC:
            return self._sync_client

    def get_database(self, connection: Connection = Connection.ASYNC):
        """Get the specific database object."""
        client = self.get(connection)
        return client[self.config.connection.database]

    async def dispose(self):
        self._async_client.close()
        self._sync_client.close()
