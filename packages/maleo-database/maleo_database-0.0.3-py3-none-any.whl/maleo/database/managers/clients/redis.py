from redis.asyncio import Redis as AsyncRedis
from redis import Redis as SyncRedis
from typing import Literal, Union, overload
from ...config import RedisDatabaseConfig
from ...enums import Connection


class RedisClientManager:
    def __init__(self, config: RedisDatabaseConfig) -> None:
        self.config = config
        self._async_client: AsyncRedis = self._init(Connection.ASYNC)
        self._sync_client: SyncRedis = self._init(Connection.SYNC)

    @overload
    def _init(self, connection: Literal[Connection.ASYNC]) -> AsyncRedis: ...
    @overload
    def _init(self, connection: Literal[Connection.SYNC]) -> SyncRedis: ...
    def _init(
        self, connection: Connection = Connection.ASYNC
    ) -> Union[AsyncRedis, SyncRedis]:
        url = self.config.connection.make_url(connection)

        # Redis clients expect different parameter names
        pooling_config = self.config.pooling.model_dump(exclude_none=True)
        redis_kwargs = {
            "max_connections": pooling_config.get("max_connections"),
            "retry_on_timeout": pooling_config.get("retry_on_timeout"),
            "connection_timeout": pooling_config.get("connection_timeout"),
            "socket_timeout": pooling_config.get("socket_timeout"),
            "socket_keepalive": pooling_config.get("socket_keepalive"),
            "decode_responses": pooling_config.get("decode_responses"),
            # health_check_interval doesn't apply to from_url method
        }
        redis_kwargs = {k: v for k, v in redis_kwargs.items() if v is not None}

        if connection is Connection.ASYNC:
            self._async_client = AsyncRedis.from_url(url, **redis_kwargs)
            return self._async_client
        else:
            self._sync_client = SyncRedis.from_url(url, **redis_kwargs)
            return self._sync_client

    @overload
    def get(self, connection: Literal[Connection.ASYNC]) -> AsyncRedis: ...
    @overload
    def get(self, connection: Literal[Connection.SYNC]) -> SyncRedis: ...
    def get(
        self, connection: Connection = Connection.ASYNC
    ) -> Union[AsyncRedis, SyncRedis]:
        if connection is Connection.ASYNC:
            return self._async_client
        elif connection is Connection.SYNC:
            return self._sync_client

    async def dispose(self):
        await self._async_client.close()
        self._sync_client.close()
