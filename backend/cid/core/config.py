"""Typed settings, loaded with precedence: env vars > .env (repo root) > config/cid.yaml > hard fallbacks.

The hard fallbacks match docker-compose.yml's fallback values exactly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import dotenv_values

REPO_ROOT = Path(__file__).resolve().parents[3]

_FALLBACKS = {
    "POSTGRES_USER": "cid",
    "POSTGRES_PASSWORD": "cidlocaldev",
    "POSTGRES_DB": "cid",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "NEO4J_URI": "bolt://localhost:7687",
    "NEO4J_USER": "neo4j",
    "NEO4J_PASSWORD": "cidlocaldev",
}


def _resolve(key: str, dotenv_map: dict[str, str | None]) -> str:
    if key in os.environ:
        return os.environ[key]
    if dotenv_map.get(key):
        return dotenv_map[key]  # type: ignore[return-value]
    return _FALLBACKS[key]


@dataclass(frozen=True)
class WorldConfig:
    people: int
    firs: int
    cdr_rows: int
    txns: int
    towers: int
    background_networks: int
    synthetic_threshold_inr: int


@dataclass(frozen=True)
class ExtractConfig:
    backend: str


@dataclass(frozen=True)
class ErConfig:
    auto_merge: float
    review_min: float
    sbert_model: str


@dataclass(frozen=True)
class NlpConfig:
    encoder: str


@dataclass(frozen=True)
class CopresenceConfig:
    window_minutes: int
    dbscan_eps: float
    dbscan_min_samples: int
    night_hours: list[int]


@dataclass(frozen=True)
class AnalyticsConfig:
    case_hops: int
    kpp_k: int
    bundle_threshold: int
    max_nodes: int


@dataclass(frozen=True)
class HgtConfig:
    hidden: int
    heads: int
    layers: int
    epochs: int
    lr: float


@dataclass(frozen=True)
class LinkpredConfig:
    min_score: float
    max_per_case: int


@dataclass(frozen=True)
class ExplainConfig:
    epochs: int
    top_k_edges: int


@dataclass(frozen=True)
class RiskConfidenceConfig:
    high_documented_share: float
    medium_documented_share: float
    high_min_resolution: float


@dataclass(frozen=True)
class RiskConfig:
    weights: dict[str, float]
    confidence: RiskConfidenceConfig


@dataclass(frozen=True)
class Settings:
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str

    seed: int
    world: WorldConfig
    extract: ExtractConfig
    er: ErConfig
    nlp: NlpConfig
    copresence: CopresenceConfig
    analytics: AnalyticsConfig
    hgt: HgtConfig
    linkpred: LinkpredConfig
    explain: ExplainConfig
    risk: RiskConfig


def get_settings(repo_root: Path = REPO_ROOT) -> Settings:
    """Build a fresh Settings object, re-reading .env / env vars each call."""
    dotenv_path = repo_root / ".env"
    dotenv_map = dotenv_values(dotenv_path) if dotenv_path.exists() else {}

    yaml_path = repo_root / "config" / "cid.yaml"
    with yaml_path.open() as f:
        raw = yaml.safe_load(f)

    return Settings(
        postgres_user=_resolve("POSTGRES_USER", dotenv_map),
        postgres_password=_resolve("POSTGRES_PASSWORD", dotenv_map),
        postgres_db=_resolve("POSTGRES_DB", dotenv_map),
        postgres_host=_resolve("POSTGRES_HOST", dotenv_map),
        postgres_port=int(_resolve("POSTGRES_PORT", dotenv_map)),
        neo4j_uri=_resolve("NEO4J_URI", dotenv_map),
        neo4j_user=_resolve("NEO4J_USER", dotenv_map),
        neo4j_password=_resolve("NEO4J_PASSWORD", dotenv_map),
        seed=raw["seed"],
        world=WorldConfig(**raw["world"]),
        extract=ExtractConfig(**raw["extract"]),
        er=ErConfig(**raw["er"]),
        nlp=NlpConfig(**raw["nlp"]),
        copresence=CopresenceConfig(**raw["copresence"]),
        analytics=AnalyticsConfig(**raw["analytics"]),
        hgt=HgtConfig(**raw["hgt"]),
        linkpred=LinkpredConfig(**raw["linkpred"]),
        explain=ExplainConfig(**raw["explain"]),
        risk=RiskConfig(
            weights=raw["risk"]["weights"],
            confidence=RiskConfidenceConfig(**raw["risk"]["confidence"]),
        ),
    )
