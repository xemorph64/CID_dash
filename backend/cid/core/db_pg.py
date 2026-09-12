"""Thin Postgres connection helper. No ORM, no pool — one connection per call."""

from __future__ import annotations

import psycopg

from cid.core.config import get_settings


def get_connection() -> psycopg.Connection:
    s = get_settings()
    return psycopg.connect(
        host=s.postgres_host,
        port=s.postgres_port,
        user=s.postgres_user,
        password=s.postgres_password,
        dbname=s.postgres_db,
    )
