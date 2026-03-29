from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from fastapi import HTTPException
import os

Base = declarative_base()

def get_database_url():
    """Get database URL from environment only"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable is required")
        raise ValueError("DATABASE_URL environment variable is required")
    return database_url

# Get database URL safely
try:
    database_url = get_database_url()
    print(f"✅ Database URL configured: {database_url.split('@')[1] if '@' in database_url else 'configured'}")
except Exception as e:
    print(f"❌ Database configuration error: {e}")
    database_url = None

# Async engine for API operations
async_engine = None
AsyncSessionLocal = None

if database_url:
    try:
        async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        async_engine = create_async_engine(async_database_url, echo=False, future=True)
        AsyncSessionLocal = async_sessionmaker(
            async_engine, class_=AsyncSession, expire_on_commit=False
        )
        print("✅ Async database engine initialized")
    except Exception as e:
        print(f"❌ Failed to initialize async database engine: {e}")
        async_engine = None
        AsyncSessionLocal = None

# Sync engine for table creation
sync_engine = None
SessionLocal = None

if database_url:
    try:
        sync_engine = create_engine(database_url, echo=False, future=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
        print("✅ Sync database engine initialized")
    except Exception as e:
        print(f"❌ Failed to initialize sync database engine: {e}")
        sync_engine = None
        SessionLocal = None

def create_tables():
    """Create all database tables using sync engine"""
    if not sync_engine:
        print("❌ Cannot create tables: database engine not initialized")
        return False
    
    try:
        print("🔄 Creating database tables...")
        Base.metadata.create_all(bind=sync_engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        return False

async def get_db():
    """Get async database session"""
    if not AsyncSessionLocal:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    async with AsyncSessionLocal() as session:
        yield session