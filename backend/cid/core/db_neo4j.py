"""Thin Neo4j driver helper."""

from __future__ import annotations

from neo4j import Driver, GraphDatabase

from cid.core.config import get_settings


def get_driver() -> Driver:
    s = get_settings()
    return GraphDatabase.driver(s.neo4j_uri, auth=(s.neo4j_user, s.neo4j_password))
