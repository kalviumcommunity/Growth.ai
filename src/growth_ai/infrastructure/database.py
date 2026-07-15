from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def create_engine_from_url(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True, future=True)


def verify_database_connection(database_url: str) -> None:
    engine = create_engine_from_url(database_url)
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
