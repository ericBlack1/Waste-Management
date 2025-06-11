from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Replace psycopg2 with asyncpg in the connection string
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", 
    "postgresql+asyncpg://"
)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  # Set to False in production
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db

# Sync dependency (for existing auth)
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

# Keep your existing sync engine for migrations if needed
from sqlalchemy import create_engine
sync_engine = create_engine(settings.DATABASE_URL)