// Constraints and indexes only — no data. Neo4j 5 syntax; safe to re-run.
// Per architecture.md §5.2.

CREATE CONSTRAINT person_entity_id IF NOT EXISTS FOR (n:Person) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT organization_entity_id IF NOT EXISTS FOR (n:Organization) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT bankaccount_entity_id IF NOT EXISTS FOR (n:BankAccount) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT phonenumber_entity_id IF NOT EXISTS FOR (n:PhoneNumber) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT vehicle_entity_id IF NOT EXISTS FOR (n:Vehicle) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT location_entity_id IF NOT EXISTS FOR (n:Location) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT event_entity_id IF NOT EXISTS FOR (n:Event) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT device_entity_id IF NOT EXISTS FOR (n:Device) REQUIRE n.entity_id IS UNIQUE;

// Neo4j 5 requires a relationship type per index (no wildcard type) — one per
// relationship type in §5.2, all indexing the same common-set property.
CREATE INDEX rel_edge_id_accused_in IF NOT EXISTS FOR ()-[r:ACCUSED_IN]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_victim_in IF NOT EXISTS FOR ()-[r:VICTIM_IN]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_witness_in IF NOT EXISTS FOR ()-[r:WITNESS_IN]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_owns IF NOT EXISTS FOR ()-[r:OWNS]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_director_of IF NOT EXISTS FOR ()-[r:DIRECTOR_OF]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_registered_at IF NOT EXISTS FOR ()-[r:REGISTERED_AT]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_transferred_funds_to IF NOT EXISTS FOR ()-[r:TRANSFERRED_FUNDS_TO]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_called IF NOT EXISTS FOR ()-[r:CALLED]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_registered_to IF NOT EXISTS FOR ()-[r:REGISTERED_TO]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_present_at IF NOT EXISTS FOR ()-[r:PRESENT_AT]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_associated_with IF NOT EXISTS FOR ()-[r:ASSOCIATED_WITH]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_co_located_with IF NOT EXISTS FOR ()-[r:CO_LOCATED_WITH]-() ON (r.edge_id);
CREATE INDEX rel_edge_id_ai_suggested IF NOT EXISTS FOR ()-[r:AI_SUGGESTED]-() ON (r.edge_id);

CREATE INDEX event_fir_no IF NOT EXISTS FOR (n:Event) ON (n.FIR_no);
CREATE INDEX location_entity_id IF NOT EXISTS FOR (n:Location) ON (n.entity_id);
