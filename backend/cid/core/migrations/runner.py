"""Tiny hand-rolled migration runner. No framework — run with:

    python -m cid.core.migrations.runner

Applies any .sql file in this directory not yet recorded in schema_migrations,
in filename order, each in its own transaction. Idempotent.
"""

from __future__ import annotations

from pathlib import Path

from cid.core.db_pg import get_connection

MIGRATIONS_DIR = Path(__file__).resolve().parent


def run() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    filename   text PRIMARY KEY,
                    applied_at timestamptz DEFAULT now()
                )
                """
            )
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT filename FROM schema_migrations")
            applied = {row[0] for row in cur.fetchall()}

        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if sql_file.name in applied:
                continue
            print(f"Applying {sql_file.name}...")
            sql = sql_file.read_text()
            with conn.cursor() as cur:
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (%s)",
                    (sql_file.name,),
                )
            conn.commit()


if __name__ == "__main__":
    run()
