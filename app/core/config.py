from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Multi-Protocol Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = (
        "Demonstration eines modernen Python-Backends mit FastAPI, Pydantic v2, "
        "SQLAlchemy 2.0, PostgreSQL und 3 Schnittstellen-Paradigmen: REST, GraphQL und Protobuf."
    )
    
    # Datenbankkonfiguration: Standard PostgreSQL mit automatischem SQLite Fallback
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "fastapidemo"

    # Explizite Database-URL oder Fallback-URL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapidemo"
    SQLITE_URL: str = "sqlite+aiosqlite:///./fastapidemo.db"
    
    # Erzwingt SQLite (z.B. für Tests oder schnelles lokales Ausführen ohne laufendes PostgreSQL)
    USE_SQLITE: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
