from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from typing import Literal, Tuple, Union, overload
from ...config import SQLiteDatabaseConfig
from ...enums import Connection


class SQLiteEngineManager:
    def __init__(self, config: SQLiteDatabaseConfig) -> None:
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

        # SQLite pooling is limited, most params don't apply
        pooling_kwargs = self.config.pooling.model_dump(
            exclude={"wal_mode", "busy_timeout"},  # These go in URL options
            exclude_none=True,
        )

        engine_kwargs = {"echo": self.config.connection.echo, **pooling_kwargs}

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
