-- Tables per architecture.md §5.1. Column set is the "key columns" architecture.md
-- lists for each table; later milestones may need to add columns as ALTER migrations.

CREATE TABLE source_records (
    source_record_id text PRIMARY KEY,
    source_system     text NOT NULL,
    record_type       text NOT NULL, -- fir, cdr, txn, kyc, phone_reg, company, vehicle
    legal_basis       text,
    auth_tier         text,
    ingested_at       timestamptz NOT NULL DEFAULT now(),
    raw               jsonb,
    text              text,
    record_hash       text
);

CREATE TABLE mentions (
    mention_id             text PRIMARY KEY,
    source_record_id       text NOT NULL,
    entity_type            text NOT NULL,
    surface                text NOT NULL, -- as written
    script                 text,
    start                  integer,
    "end"                  integer,
    extraction_confidence  double precision,
    resolved_entity_id     text
);

CREATE TABLE relation_mentions (
    id                     text PRIMARY KEY,
    source_record_id       text NOT NULL,
    head_mention_id        text NOT NULL,
    tail_mention_id        text NOT NULL,
    rel_type               text NOT NULL,
    start                  integer,
    "end"                  integer,
    extraction_confidence  double precision
);

CREATE TABLE entities (
    entity_id              text PRIMARY KEY,
    entity_type            text NOT NULL,
    canonical_name         text,
    resolution_confidence  double precision,
    review_status          text,
    run_id                 text
);

CREATE TABLE er_pairs (
    pair_id            text PRIMARY KEY,
    mention_a          text NOT NULL,
    mention_b          text NOT NULL,
    match_probability  double precision,
    evidence           jsonb,
    tier               text,
    decision           text,
    decided_by         text,
    decided_at         timestamptz
);

CREATE TABLE users (
    user_id        text PRIMARY KEY,
    role           text NOT NULL,
    display_name   text,
    password_hash  text
);

CREATE TABLE cases (
    case_id            text PRIMARY KEY,
    title              text,
    anchor_record_id   text,
    legal_basis        text,
    status             text
);

CREATE TABLE case_assignments (
    user_id  text NOT NULL REFERENCES users (user_id),
    case_id  text NOT NULL REFERENCES cases (case_id),
    PRIMARY KEY (user_id, case_id)
);

CREATE TABLE leads (
    lead_id                  text PRIMARY KEY,
    case_id                  text,
    status                   text,
    evidence_class_summary   jsonb,
    explanation_fidelity     jsonb,
    run_id                   text
);

CREATE TABLE lead_subgraph (
    lead_id         text NOT NULL,
    element_id      text NOT NULL,
    element_kind    text NOT NULL, -- node / edge
    evidence_class  text,
    role            text -- core / context
);

CREATE TABLE stamps (
    stamp_id     text PRIMARY KEY,
    target_kind  text NOT NULL,
    target_id    text NOT NULL,
    decision     text,
    reason       text,
    user_id      text,
    at           timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE case_items (
    case_id    text NOT NULL,
    item_kind  text NOT NULL,
    item_id    text NOT NULL,
    added_by   text,
    at         timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE audit_log (
    seq          bigserial PRIMARY KEY,
    at           timestamptz NOT NULL DEFAULT now(),
    user_id      text,
    role         text,
    case_id      text,
    legal_basis  text,
    action       text,
    target       text,
    outcome      text,
    prev_hash    text,
    entry_hash   text
);

CREATE TABLE audit_seals (
    seal_id      text PRIMARY KEY,
    from_seq     bigint NOT NULL,
    to_seq       bigint NOT NULL,
    merkle_root  text,
    at           timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE pipeline_runs (
    run_id            text PRIMARY KEY,
    seed              integer,
    config_snapshot   jsonb,
    started_at        timestamptz,
    finished_at       timestamptz,
    metrics           jsonb
);
