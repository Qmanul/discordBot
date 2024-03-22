import contextlib
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncConnection, AsyncSession
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DatabaseSessionManager:
    """
    A class that manages database connections and sessions.

    Args:
        host (str): The database connection URL.
        **engine_kwargs: Additional keyword arguments to pass to the SQLAlchemy engine.

    Attributes:
        _engine (AsyncEngine): The SQLAlchemy async engine.
        _sessionmaker (AsyncSessionMaker): The SQLAlchemy async session maker.

    """

    def __init__(self, host: str, **engine_kwargs):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine, class_=AsyncSession)

    async def close(self):
        """
        Close the database connection and session maker.

        Raises:
            Exception: If the database connection or session maker is not initialized.

        """
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """
        A context manager for a database connection.

        Yields:
            AsyncIterator[AsyncConnection]: A database connection.

        Raises:
            Exception: If the database connection or session maker is not initialized.

        """
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        A context manager for a database session.

        Yields:
            AsyncIterator[AsyncSession]: A database session.

        Raises:
            Exception: If the database connection or session maker is not initialized.

        """
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
