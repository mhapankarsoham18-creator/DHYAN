import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv

_ = load_dotenv()

from urllib.parse import urlparse, urlunparse

db_url = os.environ.get("DATABASE_URL")

if not db_url:
    print("FATAL: DATABASE_URL must be provided in .env.", file=sys.stderr)
    sys.exit(1)

# Ensure asyncpg is the dialect
parsed = urlparse(db_url)
if parsed.scheme == "postgresql" or parsed.scheme == "postgres":
    parsed = parsed._replace(scheme="postgresql+asyncpg")

DATABASE_URL = urlunparse(parsed)

# Disable echo to prevent leaking PII/Order volumes in server logs
engine = create_async_engine(DATABASE_URL, echo=False)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

SessionLocal = async_session_maker

async def get_db():
    async with async_session_maker() as session:
        yield session
