import React, { useState } from "react";
import { useApp } from "@/store/AppStore";
import { ENTITIES, RELATIONSHIPS, EVIDENCE } from "@/data/mockData";
import { ENTITY_META, entityColor, degree, buildAdjacency } from "@/lib/graphUtils";
import { ENTITIES as ALL } from "@/data/mockData";
import { Crosshair, FileText, Phone, Car, MapPin, Building2, FolderArchive, Landmark, CalendarClock, User, ArrowRight, ShieldCheck, Sparkles, StickyNote } from "lucide-react";

const ICONS = { User, Phone, Car, MapPin, Building2, FolderArchive, Landmark, CalendarClock };

export default function RightInspector() {
  const {
    selectedEntityId, selectedRelationshipId, selectEntity, selectRelationship,
    focusEntityId, setFocusEntityId, openEvidenceForRelationship, openEvidence,
    addNote, notes,
  } = useApp();

  if (selectedRelationshipId) {
    return <RelationshipInspector rid={selectedRelationshipId} />;
  }
  if (selectedEntityId) {
    return <EntityInspector eid={selectedEntityId} />;
  }
  return <EmptyInspector />;
}

function EmptyInspector() {
  return (
    <div className="flex h-full flex-col items-center justify-center p-6 text-center">
      <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-border bg-accent">
        <Crosshair className="h-5 w-5 text-muted-foreground" />
      </div>
      <p className="text-sm font-medium text-foreground">Context inspector</p>
      <p className="mt-1 max-w-[15rem] text-xs text-muted-foreground">
        Select an entity or relationship in the graph to inspect its details and supporting evidence.
      </p>
    </div>
  );
}

function EntityInspector({ eid }) {
  const { selectRelationship, setFocusEntityId, focusEntityId, addNote, notes } = useApp();
  const entity = ENTITIES.find((e) => e.id === eid);
  const adj = React.useMemo(() => buildAdjacency(ENTITIES, RELATIONSHIPS), []);
  const rels = RELATIONSHIPS.filter((r) => r.source === eid || r.target === eid);
  const Icon = ICONS[ENTITY_META[entity.type].icon];
  const color = entityColor(entity.type);
  const entityNotes = notes.filter((n) => n.scope === `entity:${eid}`);

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border p-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg" style={{ background: `hsl(${color} / 0.15)`, color: `hsl(${color})` }}>
            <Icon className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <h3 className="truncate text-sm font-semibold text-foreground">{entity.name}</h3>
            <p className="text-xs text-muted-foreground">{ENTITY_META[entity.type].label}{entity.role ? ` · ${entity.role}` : ""}</p>
          </div>
        </div>
        <div className="mt-3 flex gap-2">
          <button
            onClick={() => setFocusEntityId(focusEntityId === eid ? null : eid)}
            className="flex flex-1 items-center justify-center gap-1.5 rounded-md border border-border bg-accent px-2 py-1.5 text-xs font-medium text-foreground transition hover:bg-secondary"
          >
            <Crosshair className="h-3.5 w-3.5" /> {focusEntityId === eid ? "Exit focus" : "Focus mode"}
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin p-4">
        <Section title="Overview">
          <Stat label="Connections" value={degree(eid, adj)} />
          <Stat label="Cluster" value={entity.cluster} />
          {entity.carrier && <Stat label="Carrier" value={entity.carrier} />}
          {entity.model && <Stat label="Model" value={entity.model} />}
          {entity.region && <Stat label="Region" value={entity.region} />}
          {entity.bank && <Stat label="Bank" value={entity.bank} />}
          {entity.status && <Stat label="Status" value={entity.status} />}
        </Section>

        <Section title={`Relationships (${rels.length})`}>
          <div className="space-y-1.5">
            {rels.map((r) => {
              const otherId = r.source === eid ? r.target : r.source;
              const other = ENTITIES.find((e) => e.id === otherId);
              return (
                <button
                  key={r.id}
                  onClick={() => selectRelationship(r.id)}
                  className="flex w-full items-center gap-2 rounded-md border border-border bg-card px-2.5 py-2 text-left text-xs transition hover:border-primary/50 hover:bg-accent"
                >
                  <span className="shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium" style={{ background: `hsl(${entityColor(other.type)} / 0.15)`, color: `hsl(${entityColor(other.type)})` }}>
                    {ENTITY_META[other.type].label}
                  </span>
                  <span className="flex-1 truncate text-foreground">{other.name}</span>
                  <span className="shrink-0 text-muted-foreground">{r.type}</span>
                  {!r.documented && <Sparkles className="h-3 w-3 text-primary/70" />}
                </button>
              );
            })}
          </div>
        </Section>

        <NotesSection scope={`entity:${eid}`} notes={entityNotes} addNote={addNote} />
      </div>
    </div>
  );
}

function RelationshipInspector({ rid }) {
  const { selectEntity, openEvidenceForRelationship, selectRelationship, addNote, notes } = useApp();
  const rel = RELATIONSHIPS.find((r) => r.id === rid);
  if (!rel) return <EmptyInspector />;
  const source = ENTITIES.find((e) => e.id === rel.source);
  const target = ENTITIES.find((e) => e.id === rel.target);
  const ev = EVIDENCE.filter((e) => (rel.evidence || []).includes(e.id));
  const relNotes = notes.filter((n) => n.scope === `relationship:${rid}`);

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border p-4">
        <div className="mb-2 flex items-center gap-2">
          {rel.documented ? (
            <span className="inline-flex items-center gap-1 rounded-full bg-primary/15 px-2 py-0.5 text-[11px] font-medium text-primary"><ShieldCheck className="h-3 w-3" /> Documented</span>
          ) : (
            <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground"><Sparkles className="h-3 w-3" /> AI-inferred</span>
          )}
          <span className="text-xs text-muted-foreground">{rel.type}</span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <EntityChip entity={source} onClick={() => selectEntity(source.id)} />
          <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground" />
          <EntityChip entity={target} onClick={() => selectEntity(target.id)} />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin p-4">
        <Section title="Details">
          <Stat label="Category" value={rel.category} />
          <Stat label="First observed" value={rel.first} />
          <Stat label="Last observed" value={rel.last} />
          <Stat label="Evidence status" value={rel.documented ? "Source-backed" : "Hypothesis"} />
          {!rel.documented && <Stat label="Confidence" value={`${Math.round(rel.confidence * 100)}%`} />}
        </Section>

        {!rel.documented && rel.reason && (
          <Section title="Why inferred?">
            <p className="rounded-md border border-dashed border-border bg-muted/40 p-2.5 text-xs leading-relaxed text-muted-foreground">
              {rel.reason}
            </p>
          </Section>
        )}

        <Section title={`Supporting evidence (${ev.length})`}>
          {ev.length === 0 ? (
            <p className="text-xs text-muted-foreground">No source records directly support this inferred relationship.</p>
          ) : (
            <div className="space-y-1.5">
              {ev.map((e) => (
                <button
                  key={e.id}
                  onClick={() => openEvidenceForRelationship(rid)}
                  className="flex w-full items-center gap-2 rounded-md border border-border bg-card px-2.5 py-2 text-left text-xs transition hover:border-primary/50 hover:bg-accent"
                >
                  <FileText className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                  <span className="flex-1 truncate text-foreground">{e.ref} — {e.title}</span>
                </button>
              ))}
              <button
                onClick={() => openEvidenceForRelationship(rid)}
                className="mt-1 flex w-full items-center justify-center gap-1.5 rounded-md bg-primary px-2.5 py-2 text-xs font-medium text-primary-foreground transition hover:opacity-90"
              >
                <FileText className="h-3.5 w-3.5" /> View supporting evidence
              </button>
            </div>
          )}
        </Section>

        <NotesSection scope={`relationship:${rid}`} notes={relNotes} addNote={addNote} />
      </div>
    </div>
  );
}

function EntityChip({ entity, onClick }) {
  const color = entityColor(entity.type);
  return (
    <button onClick={onClick} className="flex min-w-0 items-center gap-1.5 rounded-md border border-border bg-card px-2 py-1 text-xs transition hover:border-primary/50">
      <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: `hsl(${color})` }} />
      <span className="truncate text-foreground">{entity.name}</span>
    </button>
  );
}

function Section({ title, children }) {
  return (
    <div className="mb-5">
      <h4 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">{title}</h4>
      {children}
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="flex items-center justify-between border-b border-border/60 py-1.5 text-xs">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium text-foreground">{value}</span>
    </div>
  );
}

function NotesSection({ scope, notes, addNote }) {
  const [text, setText] = useState("");
  const scoped = notes;
  return (
    <Section title={`Investigator notes (${scoped.length})`}>
      <div className="mb-2 flex gap-1.5">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && text.trim()) { addNote(scope, text.trim()); setText(""); } }}
          placeholder="Add a note…"
          className="flex-1 rounded-md border border-input bg-background px-2 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
        />
        <button
          onClick={() => { if (text.trim()) { addNote(scope, text.trim()); setText(""); } }}
          className="rounded-md border border-border bg-accent px-2.5 py-1.5 text-xs font-medium text-foreground transition hover:bg-secondary"
        >Add</button>
      </div>
      <div className="space-y-1.5">
        {scoped.map((n) => (
          <div key={n.id} className="rounded-md border border-border bg-muted/30 p-2 text-xs">
            <p className="text-foreground">{n.text}</p>
            <p className="mt-1 text-[10px] text-muted-foreground">{n.author} · {new Date(n.ts).toLocaleDateString()}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}