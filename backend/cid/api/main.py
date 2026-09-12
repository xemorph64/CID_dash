from fastapi import FastAPI

from cid.core.db_neo4j import get_driver
from cid.core.db_pg import get_connection

app = FastAPI(title="C.I.D.")


@app.get("/api/health")
def health() -> dict[str, str]:
    result = {"postgres": "error", "neo4j": "error"}

    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        result["postgres"] = "ok"
    except Exception:
        pass

    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                session.run("RETURN 1").single()
            result["neo4j"] = "ok"
        finally:
            driver.close()
    except Exception:
        pass

    return result
