import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
from app.core.config import settings
from app.models.base import Base

logger = logging.getLogger(__name__)

# Bestimme anfängliche Datenbank-URL
initial_url = settings.SQLITE_URL if settings.USE_SQLITE else settings.DATABASE_URL
engine = create_async_engine(initial_url, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    """
    Initialisiert die Datenbank-Tabellen.
    Falls die Verbindung zu PostgreSQL fehlschlägt (z.B. lokaler Docker-Container läuft noch nicht),
    wird automatisch auf SQLite zurückgegriffen, damit die Demo unterbrechungsfrei läuft.
    """
    global engine, AsyncSessionLocal

    if not settings.USE_SQLITE:
        try:
            # Verbindungstest zu PostgreSQL
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("✅ Erfolgreich mit PostgreSQL verbunden.")
        except Exception as e:
            logger.warning(
                f"⚠️ PostgreSQL nicht erreichbar ({e}). "
                f"Schalte automatisch auf lokalen SQLite-Fallback um ({settings.SQLITE_URL})."
            )
            # Auf SQLite wechseln
            await engine.dispose()
            settings.USE_SQLITE = True
            engine = create_async_engine(settings.SQLITE_URL, echo=False, future=True)
            AsyncSessionLocal = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )

    # Tabellen anlegen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Datenbank-Tabellen erfolgreich synchronisiert.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency: Stellt eine asynchrone SQLAlchemy-Session bereit
    und führt automatisches Commit/Rollback durch.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_db() -> None:
    """Schließt die Engine sauber bei App-Shutdown."""
    if engine:
        await engine.dispose()
