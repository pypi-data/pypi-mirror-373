from elasticsearch import AsyncElasticsearch, Elasticsearch
from typing import Literal, Union, overload
from ...config import ElasticsearchDatabaseConfig
from ...enums import Connection


class ElasticsearchClientManager:
    def __init__(self, config: ElasticsearchDatabaseConfig) -> None:
        self.config = config
        self._async_client: AsyncElasticsearch = self._init(Connection.ASYNC)
        self._sync_client: Elasticsearch = self._init(Connection.SYNC)

    @overload
    def _init(self, connection: Literal[Connection.ASYNC]) -> AsyncElasticsearch: ...
    @overload
    def _init(self, connection: Literal[Connection.SYNC]) -> Elasticsearch: ...
    def _init(
        self, connection: Connection = Connection.ASYNC
    ) -> Union[AsyncElasticsearch, Elasticsearch]:
        hosts = [
            {"host": self.config.connection.host, "port": self.config.connection.port}
        ]

        # Build auth and pooling params properly
        client_kwargs = {}

        if self.config.connection.username and self.config.connection.password:
            client_kwargs["http_auth"] = (
                self.config.connection.username,
                self.config.connection.password,
            )

        # Use pooling config directly
        pooling_kwargs = self.config.pooling.model_dump(
            exclude={
                "connections_per_node",
                "block",
                "headers",
                "dead_timeout",
            },  # ES-specific excludes
            exclude_none=True,
        )
        client_kwargs.update(pooling_kwargs)

        if connection is Connection.ASYNC:
            self._async_client = AsyncElasticsearch(hosts, **client_kwargs)
            return self._async_client
        else:
            self._sync_client = Elasticsearch(hosts, **client_kwargs)
            return self._sync_client

    @overload
    def get(self, connection: Literal[Connection.ASYNC]) -> AsyncElasticsearch: ...
    @overload
    def get(self, connection: Literal[Connection.SYNC]) -> Elasticsearch: ...
    def get(
        self, connection: Connection = Connection.ASYNC
    ) -> Union[AsyncElasticsearch, Elasticsearch]:
        if connection is Connection.ASYNC:
            return self._async_client or self._init(Connection.ASYNC)
        else:
            return self._sync_client or self._init(Connection.SYNC)

    async def dispose(self):
        await self._async_client.close()
        self._sync_client.close()
