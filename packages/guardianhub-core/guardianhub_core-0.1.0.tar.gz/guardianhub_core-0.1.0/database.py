import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# PostgreSQL connection settings
_POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres-service")
_POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
_POSTGRES_DB = os.getenv("POSTGRES_DB", "guardian_db")
_POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
_POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# Construct the database URL
DATABASE_URL = f"postgresql+asyncpg://{_POSTGRES_USER}:{_POSTGRES_PASSWORD}@{_POSTGRES_HOST}:{_POSTGRES_PORT}/{_POSTGRES_DB}"

# For logging (optional but recommended)
masked_db_url = DATABASE_URL.replace(str(_POSTGRES_PASSWORD), '********') if _POSTGRES_PASSWORD else DATABASE_URL
print(f"Connecting to database: {masked_db_url}")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,  # Adjust based on your needs
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800  # Recycle connections after 30 minutes
)

# Create async session factory
async_session_factory = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise