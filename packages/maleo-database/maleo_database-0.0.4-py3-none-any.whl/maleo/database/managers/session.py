from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    asynccontextmanager,
    contextmanager,
)
from datetime import datetime, timezone
from pydantic import ValidationError
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from typing import AsyncGenerator, Generator, Literal, Tuple, Union, overload
from uuid import UUID, uuid4
from maleo.mixins.timestamp import OperationTimestamp
from maleo.types.base.uuid import OptionalUUID
from maleo.logging.logger import Database
from ..enums import Connection
from ..config import (
    PostgreSQLDatabaseConfig,
    MySQLDatabaseConfig,
    SQLiteDatabaseConfig,
    SQLServerDatabaseConfig,
)


class SessionManager:
    def __init__(
        self,
        config: Union[
            PostgreSQLDatabaseConfig,
            MySQLDatabaseConfig,
            SQLiteDatabaseConfig,
            SQLServerDatabaseConfig,
        ],
        engines: Tuple[AsyncEngine, Engine],
        logger: Database,
    ) -> None:
        self._config = config
        self._async_engine, self._sync_engine = engines
        self._logger = logger
        self._async_sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker[
            AsyncSession
        ](bind=self._async_engine, expire_on_commit=True)
        self._sync_sessionmaker: sessionmaker[Session] = sessionmaker[Session](
            bind=self._sync_engine, expire_on_commit=True
        )

    async def _async_session_handler(
        self, operation_id: UUID
    ) -> AsyncGenerator[AsyncSession, None]:
        """Async session handler with proper error handling."""
        executed_at = datetime.now(tz=timezone.utc)
        session = self._async_sessionmaker()
        try:
            yield session
            await session.commit()
            completed_at = datetime.now(tz=timezone.utc)
            self._logger.info(
                f"Operation {operation_id} - success - Committed async database transaction",
                extra={
                    "json_fields": {
                        "config": self._config.model_dump(mode="json"),
                        "operation_id": operation_id,
                        "success": True,
                        "timestamp": OperationTimestamp(
                            executed_at=executed_at,
                            completed_at=completed_at,
                            duration=(completed_at - executed_at).total_seconds(),
                        ).model_dump(mode="json"),
                    },
                },
            )
        except (SQLAlchemyError, ValidationError, Exception):
            await session.rollback()
            completed_at = datetime.now(tz=timezone.utc)
            self._logger.error(
                f"Operation {operation_id} - failed - Error handling async database session",
                exc_info=True,
                extra={
                    "json_fields": {
                        "config": self._config.model_dump(mode="json"),
                        "operation_id": operation_id,
                        "success": False,
                        "timestamp": OperationTimestamp(
                            executed_at=executed_at,
                            completed_at=completed_at,
                            duration=(completed_at - executed_at).total_seconds(),
                        ).model_dump(mode="json"),
                    },
                },
            )
            raise
        finally:
            await session.close()
            completed_at = datetime.now(tz=timezone.utc)
            self._logger.info(
                f"Operation {operation_id} - success - Closed async database session",
                extra={
                    "json_fields": {
                        "config": self._config.model_dump(mode="json"),
                        "operation_id": operation_id,
                        "success": True,
                        "timestamp": OperationTimestamp(
                            executed_at=executed_at,
                            completed_at=completed_at,
                            duration=(completed_at - executed_at).total_seconds(),
                        ).model_dump(mode="json"),
                    },
                },
            )

    def _sync_session_handler(
        self, operation_id: UUID
    ) -> Generator[Session, None, None]:
        """Sync session handler with proper error handling."""
        executed_at = datetime.now(tz=timezone.utc)
        session = self._sync_sessionmaker()
        try:
            yield session
            session.commit()
            completed_at = datetime.now(tz=timezone.utc)
            self._logger.info(
                f"Operation {operation_id} - success - Committed sync database transaction",
                extra={
                    "json_fields": {
                        "config": self._config.model_dump(mode="json"),
                        "operation_id": operation_id,
                        "success": True,
                        "timestamp": OperationTimestamp(
                            executed_at=executed_at,
                            completed_at=completed_at,
                            duration=(completed_at - executed_at).total_seconds(),
                        ).model_dump(mode="json"),
                    },
                },
            )
        except (SQLAlchemyError, ValidationError, Exception):
            session.rollback()
            completed_at = datetime.now(tz=timezone.utc)
            self._logger.error(
                f"Operation {operation_id} - failed - Error handling sync database session",
                exc_info=True,
                extra={
                    "json_fields": {
                        "config": self._config.model_dump(mode="json"),
                        "operation_id": operation_id,
                        "success": False,
                        "timestamp": OperationTimestamp(
                            executed_at=executed_at,
                            completed_at=completed_at,
                            duration=(completed_at - executed_at).total_seconds(),
                        ).model_dump(mode="json"),
                    },
                },
            )
            raise
        finally:
            session.close()
            completed_at = datetime.now(tz=timezone.utc)
            self._logger.info(
                f"Operation {operation_id} - success - Closed sync database session",
                extra={
                    "json_fields": {
                        "config": self._config.model_dump(mode="json"),
                        "operation_id": operation_id,
                        "success": True,
                        "timestamp": OperationTimestamp(
                            executed_at=executed_at,
                            completed_at=completed_at,
                            duration=(completed_at - executed_at).total_seconds(),
                        ).model_dump(mode="json"),
                    },
                },
            )

    @asynccontextmanager
    async def _async_context_manager(
        self, operation_id: UUID
    ) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager implementation."""
        async for session in self._async_session_handler(operation_id):
            yield session

    @contextmanager
    def _sync_context_manager(
        self, operation_id: UUID
    ) -> Generator[Session, None, None]:
        """Sync context manager implementation."""
        yield from self._sync_session_handler(operation_id)

    # Overloaded context manager methods
    @overload
    def get(
        self, connection: Literal[Connection.ASYNC], operation_id: OptionalUUID = None
    ) -> AbstractAsyncContextManager[AsyncSession]: ...

    @overload
    def get(
        self, connection: Literal[Connection.SYNC], operation_id: OptionalUUID = None
    ) -> AbstractContextManager[Session]: ...

    def get(
        self,
        connection: Connection = Connection.ASYNC,
        operation_id: OptionalUUID = None,
    ) -> Union[
        AbstractAsyncContextManager[AsyncSession], AbstractContextManager[Session]
    ]:
        """Context manager for manual session handling."""
        if operation_id is None:
            operation_id = uuid4()
        if connection is Connection.ASYNC:
            return self._async_context_manager(operation_id)
        else:
            return self._sync_context_manager(operation_id)

    # Alternative: More explicit methods
    @asynccontextmanager
    async def get_async(
        self, operation_id: OptionalUUID = None
    ) -> AsyncGenerator[AsyncSession, None]:
        """Explicit async context manager."""
        if operation_id is None:
            operation_id = uuid4()
        async for session in self._async_session_handler(operation_id):
            yield session

    @contextmanager
    def get_sync(
        self, operation_id: OptionalUUID = None
    ) -> Generator[Session, None, None]:
        """Explicit sync context manager."""
        if operation_id is None:
            operation_id = uuid4()
        yield from self._sync_session_handler(operation_id)

    def as_async_dependency(self, operation_id: OptionalUUID = None):
        """Explicit async dependency injection."""
        if operation_id is None:
            operation_id = uuid4()

        def dependency() -> AsyncGenerator[AsyncSession, None]:
            return self._async_session_handler(operation_id)

        return dependency

    def as_sync_dependency(self, operation_id: OptionalUUID = None):
        """Explicit sync dependency injection."""
        if operation_id is None:
            operation_id = uuid4()

        def dependency() -> AsyncGenerator[AsyncSession, None]:
            return self._async_session_handler(operation_id)

        return dependency
