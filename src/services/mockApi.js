// Simulated async service layer. Small artificial delays on first-load calls.
import {
  INVESTIGATIONS, ENTITIES, RELATIONSHIPS, EVIDENCE,
  TIMELINE_EVENTS, LEADS, NOTES, RECENTLY_VIEWED, PINNED, SAVED_LEADS,
} from "@/data/mockData";

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const mockApi = {
  async getInvestigations() {
    await delay(220);
    return INVESTIGATIONS;
  },
  async getInvestigationById(id) {
    await delay(160);
    return INVESTIGATIONS.find((i) => i.id === id) || null;
  },
  async searchEntities(query) {
    await delay(180);
    if (!query) return [];
    const q = query.toLowerCase();
    return ENTITIES.filter(
      (e) => e.name.toLowerCase().includes(q) || (e.type && e.type.includes(q)) || (e.role || "").toLowerCase().includes(q)
    ).slice(0, 20);
  },
  async getEntityById(id) {
    await delay(80);
    return ENTITIES.find((e) => e.id === id) || null;
  },
  async getNetwork(investigationId) {
    await delay(260);
    return { entities: ENTITIES, relationships: RELATIONSHIPS };
  },
  async getRelationships(entityId) {
    await delay(120);
    return RELATIONSHIPS.filter((r) => r.source === entityId || r.target === entityId);
  },
  async getEvidenceForRelationship(relationshipId) {
    await delay(120);
    const rel = RELATIONSHIPS.find((r) => r.id === relationshipId);
    if (!rel) return [];
    return EVIDENCE.filter((e) => (rel.evidence || []).includes(e.id));
  },
  async getEvidenceById(id) {
    await delay(80);
    return EVIDENCE.find((e) => e.id === id) || null;
  },
  async getTimelineEvents() {
    await delay(200);
    return TIMELINE_EVENTS;
  },
  async getLeads() {
    await delay(220);
    return LEADS;
  },
  async saveLead(leadId) {
    await delay(80);
    return { ok: true, leadId };
  },
  async updateLeadStatus(leadId, status) {
    await delay(80);
    const lead = LEADS.find((l) => l.id === leadId);
    if (lead) lead.status = status;
    return { ok: true, leadId, status };
  },
  async createInvestigation(input) {
    await delay(200);
    return { id: `inv-${Date.now()}`, ...input, status: "active" };
  },
  async getNotes() {
    await delay(120);
    return NOTES;
  },
  async saveInvestigationNote(input) {
    await delay(80);
    return { id: `N${Date.now()}`, ...input };
  },
  async getRecentlyViewed() {
    await delay(120);
    return RECENTLY_VIEWED;
  },
  async getPinned() {
    await delay(80);
    return PINNED;
  },
  async getSavedLeads() {
    await delay(80);
    return SAVED_LEADS;
  },
  // Disruption + pathfinding are computed locally (graphUtils) — no delay needed,
  // but we keep a tiny one so loading states can show.
  async simulateDisruption() {
    await delay(120);
    return { ok: true };
  },
  async findPaths() {
    await delay(120);
    return { ok: true };
  },
};

export default mockApi;