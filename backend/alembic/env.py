"""Alembic environment configuration for async migrations."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import get_settings
from app.database import Base

# Import all models so they're registered with Base.metadata
from app.auth.models import User, UserSession  # noqa: F401
from app.organizations.models import Organization  # noqa: F401
from app.applications.models import (  # noqa: F401
    FundingApplication,
    ApplicationSection,
    ApplicationStatusHistory,
    ApplicationComment,
)
from app.documents.models import Document  # noqa: F401
from app.reviews.models import Review, ReviewScore  # noqa: F401
from app.vulnerability.models import (  # noqa: F401
    IndicatorCategory,
    Indicator,
    DataSource,
    IndicatorValue,
    SVIScore,
)
from app.ingestion.models import IngestionJob  # noqa: F401
from app.geography.models import Region, Municipality  # noqa: F401
from app.common.audit import AuditLog  # noqa: F401

config = context.config
settings = get_settings()

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Override sqlalchemy.url with app settings
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
