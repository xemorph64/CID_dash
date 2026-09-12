from cid.core.db_pg import get_connection
from cid.core.migrations.runner import run

EXPECTED_TABLES = {
    "source_records",
    "mentions",
    "relation_mentions",
    "entities",
    "er_pairs",
    "users",
    "case_assignments",
    "cases",
    "leads",
    "lead_subgraph",
    "stamps",
    "case_items",
    "audit_log",
    "audit_seals",
    "pipeline_runs",
}


def _table_names() -> set[str]:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        return {row[0] for row in cur.fetchall()}


def test_migrations_create_all_tables():
    run()
    assert EXPECTED_TABLES <= _table_names()


def test_migrations_are_idempotent():
    run()
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM schema_migrations")
        before = cur.fetchone()[0]

    run()

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM schema_migrations")
        after = cur.fetchone()[0]

    assert after == before
