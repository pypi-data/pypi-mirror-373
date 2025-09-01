from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    asynccontextmanager,
    contextmanager,
)
from pydantic import ValidationError
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from typing import AsyncGenerator, Generator, Literal, Tuple, Union, overload
from ..enums import Connection


class SessionManager:
    def __init__(self, engines: Tuple[AsyncEngine, Engine]) -> None:
        self._async_engine, self._sync_engine = engines
        self._async_sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker[
            AsyncSession
        ](bind=self._async_engine, expire_on_commit=True)
        self._sync_sessionmaker: sessionmaker[Session] = sessionmaker[Session](
            bind=self._sync_engine, expire_on_commit=True
        )

    async def _async_session_handler(self) -> AsyncGenerator[AsyncSession, None]:
        """Async session handler with proper error handling."""
        session = self._async_sessionmaker()
        try:
            yield session
            await session.commit()
        except (SQLAlchemyError, ValidationError, Exception):
            await session.rollback()
            raise
        finally:
            await session.close()

    def _sync_session_handler(self) -> Generator[Session, None, None]:
        """Sync session handler with proper error handling."""
        session = self._sync_sessionmaker()
        try:
            yield session
            session.commit()
        except (SQLAlchemyError, ValidationError, Exception):
            session.rollback()
            raise
        finally:
            session.close()

    # Overloaded context manager methods
    @overload
    def get(
        self, connection: Literal[Connection.ASYNC]
    ) -> AbstractAsyncContextManager[AsyncSession]: ...

    @overload
    def get(
        self, connection: Literal[Connection.SYNC]
    ) -> AbstractContextManager[Session]: ...

    def get(
        self, connection: Connection = Connection.ASYNC
    ) -> Union[
        AbstractAsyncContextManager[AsyncSession], AbstractContextManager[Session]
    ]:
        """Context manager for manual session handling."""
        if connection is Connection.ASYNC:
            return self._async_context_manager()
        else:
            return self._sync_context_manager()

    @asynccontextmanager
    async def _async_context_manager(self) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager implementation."""
        async for session in self._async_session_handler():
            yield session

    @contextmanager
    def _sync_context_manager(self) -> Generator[Session, None, None]:
        """Sync context manager implementation."""
        yield from self._sync_session_handler()

    # Alternative: More explicit methods
    @asynccontextmanager
    async def get_async(self) -> AsyncGenerator[AsyncSession, None]:
        """Explicit async context manager."""
        async for session in self._async_session_handler():
            yield session

    @contextmanager
    def get_sync(self) -> Generator[Session, None, None]:
        """Explicit sync context manager."""
        yield from self._sync_session_handler()
        # with self._sync_session_handler() as session:
        #     yield session

    def inject_async(self) -> AsyncGenerator[AsyncSession, None]:
        """Explicit async dependency injection."""
        return self._async_session_handler()

    def inject_sync(self) -> Generator[Session, None, None]:
        """Explicit sync dependency injection."""
        return self._sync_session_handler()
