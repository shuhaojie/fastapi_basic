import os
import sys

# 将项目根目录添加到 Python 路径
print(os.path.abspath(os.path.join(os.getcwd(), "app")))
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "app")))

from app.db import Base  # noqa
from logging.config import fileConfig  # noqa
from sqlalchemy import engine_from_config  # noqa
from sqlalchemy import pool  # noqa
from alembic import context  # noqa


config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.users import models  # noqa
from app.auth import models  # noqa

target_metadata = Base.metadata
print("Detected tables in metadata:", list(target_metadata.tables.keys()))


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


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
