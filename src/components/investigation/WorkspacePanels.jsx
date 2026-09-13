import React, { useMemo } from "react";
import { useApp } from "@/store/AppStore";
import { ENTITIES, RELATIONSHIPS, EVIDENCE, TIMELINE_EVENTS, INVESTIGATIONS } from "@/data/mockData";
import { entityColor, ENTITY_META, degree, buildAdjacency } from "@/lib/graphUtils";
import { Search, FileText, ShieldCheck, Sparkles, Clock, ArrowRight } from "lucide-react";

export function CaseOverview() {
  const { currentInvestigationId, selectEntity, openEvidence } = useApp();
  const inv = INVESTIGATIONS.find((i) => i.id === currentInvestigationId);
  const adj = useMemo(() => buildAdjacency(ENTITIES, RELATIONSHIPS), []);
  const topEntities = [...ENTITIES].map((e) => ({ ...e, deg: degree(e.id, adj) })).sort((a, b) => b.deg - a.deg).slice(0, 6);

  return (
    <div className="h-full overflow-y-auto scrollbar-thin p-6">
      <div className="mx-auto max-w-3xl">
        <div className="mb-6 rounded-xl border border-border bg-card p-5">
          <div className="mb-2 flex items-center gap-2">
            <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-[10px] font-medium text-amber-500">DEMO</span>
            <h2 className="text-lg font-semibold text-foreground">{inv?.title}</h2>
          </div>
          <p className="text-sm leading-relaxed text-muted-foreground">{inv?.summary}</p>
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Mini label="Opened" value={inv?.opened} />
            <Mini label="Lead" value={inv?.lead} />
            <Mini label="Status" value={inv?.status} />
            <Mini label="Entities" value={ENTITIES.length} />
          </div>
        </div>

        <div className="mb-4 rounded-xl border border-dashed border-primary/30 bg-primary/5 p-4">
          <div className="mb-1 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-foreground">Intelligence Brief</span>
          </div>
          <p className="text-xs leading-relaxed text-foreground/85">
            The network centers on <button className="font-medium text-primary underline-offset-2 hover:underline" onClick={() => selectEntity("P1")}>Ravi Menon</button>, who bridges coastal logistics and urban finance clusters.
            The strongest inferred link is P1↔P3 (confidence 71%), supported by aligned port meetings and Zenith account inflows.
            Two documented bridges (P1→P2 calls, A1→A2 transfers) connect the logistics and finance clusters.
          </p>
          <p className="mt-2 text-[11px] text-muted-foreground">AI-generated summary — verify against source evidence.</p>
        </div>

        <h3 className="mb-2 text-sm font-medium text-foreground">Most connected entities</h3>
        <div className="grid gap-2 sm:grid-cols-2">
          {topEntities.map((e) => (
            <button key={e.id} onClick={() => selectEntity(e.id)} className="flex items-center gap-3 rounded-lg border border-border bg-card p-3 text-left transition hover:bg-accent">
              <span className="h-2.5 w-2.5 rounded-full" style={{ background: `hsl(${entityColor(e.type)})` }} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm text-foreground">{e.name}</p>
                <p className="text-[11px] text-muted-foreground">{ENTITY_META[e.type].label}{e.role ? ` · ${e.role}` : ""}</p>
              </div>
              <span className="text-sm font-semibold text-primary">{e.deg}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export function EntityList() {
  const { selectEntity } = useApp();
  const [q, setQ] = React.useState("");
  const filtered = ENTITIES.filter((e) => e.name.toLowerCase().includes(q.toLowerCase()));
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border p-4">
        <div className="flex items-center gap-2 rounded-md border border-input bg-background px-3 py-2">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter entities…" className="flex-1 bg-transparent text-sm focus:outline-none" />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin p-4">
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((e) => (
            <button key={e.id} onClick={() => selectEntity(e.id)} className="flex items-center gap-2.5 rounded-lg border border-border bg-card p-3 text-left transition hover:bg-accent">
              <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: `hsl(${entityColor(e.type)})` }} />
              <div className="min-w-0">
                <p className="truncate text-sm text-foreground">{e.name}</p>
                <p className="text-[11px] text-muted-foreground">{ENTITY_META[e.type].label}</p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export function EvidenceList() {
  const { openEvidence } = useApp();
  return (
    <div className="h-full overflow-y-auto scrollbar-thin p-5">
      <div className="mx-auto max-w-3xl space-y-2">
        {EVIDENCE.map((e) => (
          <button key={e.id} onClick={() => openEvidence(e.id)} className="flex w-full items-start gap-3 rounded-lg border border-border bg-card p-3 text-left transition hover:bg-accent">
            <FileText className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-foreground">{e.ref}</span>
                {e.status === "documented" ? <ShieldCheck className="h-3 w-3 text-primary" /> : <Sparkles className="h-3 w-3 text-muted-foreground" />}
              </div>
              <p className="truncate text-xs text-muted-foreground">{e.title} · {e.date}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export function TimelineView() {
  const { selectEntity, openEvidence } = useApp();
  return (
    <div className="h-full overflow-y-auto scrollbar-thin p-6">
      <div className="mx-auto max-w-2xl">
        <div className="relative pl-6">
          <div className="absolute left-2 top-2 bottom-2 w-px bg-border" />
          {TIMELINE_EVENTS.map((t) => (
            <div key={t.id} className="relative mb-5 pb-1">
              <span className="absolute -left-[18px] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-background bg-primary" />
              <div className="flex items-center gap-2">
                <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                <span className="font-mono text-xs text-muted-foreground">{t.date}</span>
                <span className="rounded bg-accent px-1.5 py-0.5 text-[10px] capitalize text-muted-foreground">{t.kind}</span>
              </div>
              <p className="mt-1 text-sm font-medium text-foreground">{t.title}</p>
              <div className="mt-1.5 flex flex-wrap gap-1.5">
                {t.entities.map((eid) => {
                  const e = ENTITIES.find((x) => x.id === eid);
                  if (!e) return null;
                  return (
                    <button key={eid} onClick={() => selectEntity(eid)} className="flex items-center gap-1 rounded border border-border bg-accent px-1.5 py-0.5 text-[11px] transition hover:border-primary/40">
                      <span className="h-1.5 w-1.5 rounded-full" style={{ background: `hsl(${entityColor(e.type)})` }} />
                      {e.name}
                    </button>
                  );
                })}
                {t.evidence.map((eid) => {
                  const ev = EVIDENCE.find((x) => x.id === eid);
                  if (!ev) return null;
                  return (
                    <button key={eid} onClick={() => openEvidence(eid)} className="flex items-center gap-1 rounded border border-border bg-card px-1.5 py-0.5 text-[11px] transition hover:border-primary/40">
                      <FileText className="h-3 w-3" /> {ev.ref}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function ActivityView({ kind }) {
  const { selectEntity, openEvidence } = useApp();
  const rels = RELATIONSHIPS.filter((r) => r.category === kind);
  return (
    <div className="h-full overflow-y-auto scrollbar-thin p-5">
      <div className="mx-auto max-w-3xl space-y-2">
        {rels.map((r) => {
          const s = ENTITIES.find((e) => e.id === r.source);
          const t = ENTITIES.find((e) => e.id === r.target);
          return (
            <div key={r.id} className="flex items-center gap-3 rounded-lg border border-border bg-card p-3">
              <button onClick={() => selectEntity(s.id)} className="flex items-center gap-1.5 text-sm text-foreground hover:text-primary">
                <span className="h-2 w-2 rounded-full" style={{ background: `hsl(${entityColor(s.type)})` }} />
                {s.name}
              </button>
              <div className="flex items-center gap-1.5">
                {r.documented ? <ShieldCheck className="h-3.5 w-3.5 text-primary" /> : <Sparkles className="h-3.5 w-3.5 text-muted-foreground" />}
                <span className="text-xs text-muted-foreground">{r.type}</span>
                <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
              </div>
              <button onClick={() => selectEntity(t.id)} className="flex items-center gap-1.5 text-sm text-foreground hover:text-primary">
                <span className="h-2 w-2 rounded-full" style={{ background: `hsl(${entityColor(t.type)})` }} />
                {t.name}
              </button>
              <span className="ml-auto text-[11px] text-muted-foreground">{r.first} → {r.last}</span>
            </div>
          );
        })}
        {rels.length === 0 && <p className="py-10 text-center text-sm text-muted-foreground">No {kind} relationships in this dataset.</p>}
      </div>
    </div>
  );
}

function Mini({ label, value }) {
  return (
    <div className="rounded-md border border-border bg-background p-2.5">
      <p className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className="mt-0.5 text-sm font-medium text-foreground">{value}</p>
    </div>
  );
}