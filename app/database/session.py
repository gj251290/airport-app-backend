import os
import urllib.parse
import uuid

from dotenv import load_dotenv
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está definido en el archivo .env")


if "asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


parsed = urllib.parse.urlparse(DATABASE_URL)
query_params = urllib.parse.parse_qsl(parsed.query)


filtered_params = [
    (k, v) for k, v in query_params if k not in ("sslmode", "channel_binding")
]


new_query = urllib.parse.urlencode(filtered_params)


DATABASE_URL = urllib.parse.urlunparse(
    (
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment,
    )
)


def _generate_unique_stmt_name():
    """Genera nombres únicos para prepared statements para evitar conflictos de cache"""
    return f"__asyncpg_stmt_{uuid.uuid4().hex}__"


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args={
        "ssl": True,
        "prepared_statement_name_func": _generate_unique_stmt_name,
        "statement_cache_size": 0,
        "command_timeout": 60,
    },
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
