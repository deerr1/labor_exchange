from contextlib import asynccontextmanager
from functools import cached_property

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, scoped_session, sessionmaker

from config import DBSettings
from interfaces import ISQLAlchemy


class SqlAlchemySync(ISQLAlchemy):
    def __init__(self, pg_settings: DBSettings) -> None:
        self.pg_settings = pg_settings

    @cached_property
    def Session(self):  # noqa
        session_factory = sessionmaker(bind=self._build_engine(), autocommit=False, autoflush=False)
        return scoped_session(session_factory)

    def get_db(self):
        db = self.Session()
        try:
            yield db
        finally:
            db.close()

    def _build_engine(self) -> Engine:
        return create_engine(str(self.pg_settings.pg_sync_dsn))

    def __call__(self):
        db = self.Session()
        try:
            yield db
        finally:
            db.close()


class SqlAlchemyAsync(ISQLAlchemy):
    def __init__(self, pg_settings: DBSettings) -> None:
        self.pg_settings = pg_settings

    @cached_property
    def Session(self):  # noqa
        session_factory = async_sessionmaker(  # noqa
            autocommit=False,
            autoflush=False,
            bind=self._build_engine(),
            expire_on_commit=False,
        )
        return session_factory

    @asynccontextmanager
    async def get_db(self):
        db = self.Session()
        try:
            yield db
        finally:
            await db.close()

    def _build_engine(self) -> AsyncEngine:
        return create_async_engine(str(self.pg_settings.pg_async_dsn))

    async def __call__(self):
        db = self.Session()
        try:
            yield db
        finally:
            await db.close()


class Base(DeclarativeBase, MappedAsDataclass):
    pass
