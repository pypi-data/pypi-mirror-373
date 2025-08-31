from typing import AsyncGenerator, Generator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

# Lazy import to avoid errors when loading
# from raystack.conf import get_settings

# Synchronous engine (initialize lazily)
_sync_engine = None
_sync_session_factory = None

# Asynchronous engine (initialize lazily)
_async_engine = None
_async_session_factory = None

def get_sync_engine():
    global _sync_engine, _sync_session_factory
    if _sync_engine is None:
        try:
            from raystack.conf import get_settings
            _sync_engine = create_engine(get_settings().DATABASES["default"]["URL"], echo=True, future=True)
            _sync_session_factory = sessionmaker(bind=_sync_engine, class_=Session)
        except ImportError:
            raise RuntimeError("Settings are not configured")
    return _sync_engine

def get_sync_session_factory():
    global _sync_session_factory
    if _sync_session_factory is None:
        get_sync_engine()  # Ensure engine is initialized
    return _sync_session_factory

def get_async_engine():
    global _async_engine, _async_session_factory
    if _async_engine is None:
        try:
            from raystack.conf import get_settings
            if "aiosqlite" in get_settings().DATABASES["default"]["URL"] or "asyncpg" in get_settings().DATABASES["default"]["URL"] or "aiomysql" in get_settings().DATABASES["default"]["URL"]:
                _async_engine = create_async_engine(get_settings().DATABASES["default"]["URL"], echo=True, future=True)
                _async_session_factory = sessionmaker(bind=_async_engine, class_=AsyncSession)
        except ImportError:
            # If settings are not configured, leave None
            pass
        except Exception:
            # If failed to create async engine, leave None
            pass
    return _async_engine

def get_async_session_factory():
    global _async_session_factory
    if _async_session_factory is None:
        get_async_engine()  # Ensure engine is initialized
    return _async_session_factory

async def create_db_and_tables():
    async_engine = get_async_engine()
    sync_engine = get_sync_engine()
    
    if async_engine:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    else:
        # If async engine is not available, use synchronous
        SQLModel.metadata.create_all(sync_engine)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async_session_factory = get_async_session_factory()
    if async_session_factory:
        async with async_session_factory() as session:
            yield session
    else:
        raise RuntimeError("Async database engine is not configured")

def get_sync_db() -> Generator[Session, None, None]:
    sync_session_factory = get_sync_session_factory()
    with sync_session_factory() as session:
        yield session