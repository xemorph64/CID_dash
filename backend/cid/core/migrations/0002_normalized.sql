-- M2: the normalised view of each source record (phones as HMAC ids, timestamps
-- in UTC with the source timezone retained, offence codes mapped to ontology ids,
-- addresses as address_key). Raw values stay in source_records.raw, which is the
-- only place they may live (architecture.md §5.3, P-08).
ALTER TABLE source_records ADD COLUMN normalized jsonb;

-- Ingest counts rejects (a record with no legal_basis is refused, architecture §6.2)
-- and we need that count to survive the run for the metrics page.
CREATE TABLE ingest_rejects (
    source_record_id  text PRIMARY KEY,
    record_type       text NOT NULL,
    reason            text NOT NULL,
    at                timestamptz NOT NULL DEFAULT now()
);
