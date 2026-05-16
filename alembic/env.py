from logging.config import fileConfig
import asyncio
import os
import urllib.parse

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from dotenv import load_dotenv

from app.database.base import Base
import app.models  # noqa: F401

# Importar todos los modelos para que Alembic los detecte

from alembic import context

# Objeto de configuración de Alembic
config = context.config

load_dotenv()


# 1. OBTENER URL DE LA BASE DE DATOS (Prioridad: Variable de Entorno > alembic.ini)
def get_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        url = config.get_main_option("sqlalchemy.url")
    return url


def clean_url_for_asyncpg(url):
    """Asegura que la URL use el driver asyncpg y limpia parametros no soportados."""
    if not url:
        return None

    if "postgresql://" in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qsl(parsed.query)
    filtered_params = [
        (k, v) for k, v in query_params if k not in ("sslmode", "channel_binding")
    ]
    new_query = urllib.parse.urlencode(filtered_params)

    return urllib.parse.urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        )
    )


# Configurar el registro (logging)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Correr migraciones en modo 'offline'."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Función auxiliar para ejecutar migraciones en modo online."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Correr migraciones en modo 'online' usando async."""
    raw_url = get_url()
    db_url = clean_url_for_asyncpg(raw_url)

    if not db_url:
        raise ValueError("DATABASE_URL no encontrada.")

    # Crear engine asíncrono
    connectable = create_async_engine(
        db_url,
        poolclass=pool.NullPool,
        # 'ssl': True es lo que asyncpg entiende para activar el cifrado
        connect_args={"ssl": True},
    )

    async with connectable.connect() as connection:
        # Importante: usamos run_sync para que Alembic (que es síncrono)
        # pueda trabajar sobre una conexión asíncrona
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations():
    """Determinar si ejecutar en modo offline u online."""
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        # En entornos Linux (como el runner de GitHub),
        # a veces es necesario manejar el loop de esta forma
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Si ya hay un loop corriendo (raro en este script pero posible)
            asyncio.ensure_future(run_migrations_online())
        else:
            asyncio.run(run_migrations_online())


# Ejecución principal
if __name__ == "__main__":
    run_migrations()
else:
    # Alembic llama a este archivo directamente
    run_migrations()
