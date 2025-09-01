from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from typing import Literal, Tuple, Union, overload
from ...config import SQLServerDatabaseConfig
from ...enums import Connection


class SQLServerEngineManager:
    def __init__(self, config: SQLServerDatabaseConfig) -> None:
        self.config = config
        self._async_engine: AsyncEngine = self._init(Connection.ASYNC)
        self._sync_engine: Engine = self._init(Connection.SYNC)

    @overload
    def _init(self, connection: Literal[Connection.ASYNC]) -> AsyncEngine: ...
    @overload
    def _init(self, connection: Literal[Connection.SYNC]) -> Engine: ...
    def _init(
        self, connection: Connection = Connection.ASYNC
    ) -> Union[AsyncEngine, Engine]:
        url = self.config.connection.make_url(connection)

        pooling_kwargs = self.config.pooling.model_dump(
            exclude={
                "strategy",
                "connection_timeout",  # Goes in URL
                "command_timeout",  # Goes in URL
                "packet_size",  # Goes in URL
                "trust_server_certificate",  # Goes in URL
            },
            exclude_none=True,
        )

        engine_kwargs = {
            "echo": self.config.connection.echo,
            **pooling_kwargs,  # This includes encrypt, which is valid
        }

        if connection is Connection.ASYNC:
            self._async_engine = create_async_engine(url, **engine_kwargs)
            return self._async_engine
        elif connection is Connection.SYNC:
            self._sync_engine = create_engine(url, **engine_kwargs)
            return self._sync_engine

    @overload
    def get(self, connection: Literal[Connection.ASYNC]) -> AsyncEngine: ...
    @overload
    def get(self, connection: Literal[Connection.SYNC]) -> Engine: ...
    def get(
        self, connection: Connection = Connection.ASYNC
    ) -> Union[AsyncEngine, Engine]:
        if connection is Connection.ASYNC:
            return self._async_engine
        elif connection is Connection.SYNC:
            return self._sync_engine

    def get_all(self) -> Tuple[AsyncEngine, Engine]:
        return (self._async_engine, self._sync_engine)

    async def dispose(self):
        await self._async_engine.dispose()
        self._sync_engine.dispose()
