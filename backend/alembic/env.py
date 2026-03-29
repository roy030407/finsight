import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Path setup ────────────────────────────────────────────────────
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ── Load .env for local development ──────────────────────────────
load_dotenv()

# ── Import Base + all models (required for autogenerate) ──────────
from app.database.database import Base
from app.models import *  # noqa: F401, F403

# ── Alembic config object ─────────────────────────────────────────
config = context.config

# Normalise the DATABASE_URL (Render gives "postgres://", SQLAlchemy needs "postgresql://")
raw_url = os.getenv("DATABASE_URL", "")
normalised_url = raw_url.replace("postgres://", "postgresql://", 1)
config.set_main_option("sqlalchemy.url", normalised_url)

# ── Logging ───────────────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Target metadata for autogenerate ─────────────────────────────
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (offline mode)."""
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
    """Run migrations with a live DB connection (normal mode)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()