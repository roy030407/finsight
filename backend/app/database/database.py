from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

Base = declarative_base()

# Async engine for API operations
async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(async_database_url, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Sync engine for table creation
sync_engine = create_engine(settings.database_url, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

def create_tables():
    """Create all database tables using sync engine"""
    Base.metadata.create_all(bind=sync_engine)

async def get_db():
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        yield session