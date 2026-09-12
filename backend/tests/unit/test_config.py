from cid.core.config import get_settings


def test_yaml_values_load():
    s = get_settings()
    assert s.seed == 20260310
    assert s.er.auto_merge == 0.95
    assert s.er.review_min == 0.75
    assert s.analytics.max_nodes == 300


def test_env_var_overrides(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "someone_else")
    s = get_settings()
    assert s.postgres_user == "someone_else"


def test_fallback_when_nothing_set(monkeypatch):
    for key in (
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "NEO4J_URI",
        "NEO4J_USER",
        "NEO4J_PASSWORD",
    ):
        monkeypatch.delenv(key, raising=False)
    # Also hide any repo-root .env so this test is independent of local setup.
    monkeypatch.setattr("cid.core.config.dotenv_values", lambda path: {})
    s = get_settings()
    assert s.postgres_user == "cid"
    assert s.postgres_password == "cidlocaldev"
    assert s.postgres_db == "cid"
    assert s.postgres_host == "localhost"
    assert s.postgres_port == 5432
    assert s.neo4j_uri == "bolt://localhost:7687"
    assert s.neo4j_user == "neo4j"
    assert s.neo4j_password == "cidlocaldev"
