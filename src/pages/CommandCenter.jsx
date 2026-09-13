import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "@/store/AppStore";
import { INVESTIGATIONS, ENTITIES, LEADS, TIMELINE_EVENTS, EVIDENCE } from "@/data/mockData";
import { entityColor, ENTITY_META } from "@/lib/graphUtils";
import { Search, FolderArchive, Pin, Clock, ArrowRight, Lightbulb, Activity, Network, ShieldCheck, Sparkles, Command } from "lucide-react";

export default function CommandCenter() {
  const { setCurrentInvestigationId, recentlyViewed, pinned, savedLeads, setCommandPaletteOpen, selectEntity } = useApp();
  const [q, setQ] = useState("");
  const results = q ? ENTITIES.filter((e) => e.name.toLowerCase().includes(q.toLowerCase())).slice(0, 8) : [];

  const recentInvestigations = INVESTIGATIONS.filter((i) => pinned.includes(i.id));
  const savedLeadObjs = LEADS.filter((l) => savedLeads.includes(l.id));
  const recentEntities = recentlyViewed.map((id) => ENTITIES.find((e) => e.id === id)).filter(Boolean).slice(0, 6);
  const recentEvents = [...TIMELINE_EVENTS].slice(-5).reverse();

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-6xl px-6 py-8">
        {/* header */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-foreground">Command Center</h1>
              <p className="text-xs text-muted-foreground">Investigator workspace · DEMO</p>
            </div>
          </div>
          <button onClick={() => setCommandPaletteOpen(true)} className="flex items-center gap-2 rounded-md border border-border bg-card px-3 py-2 text-sm text-muted-foreground transition hover:border-primary/40 hover:text-foreground">
            <Command className="h-4 w-4" /> Command palette <kbd className="rounded border border-border bg-background px-1 text-[10px]">⌘K</kbd>
          </button>
        </div>

        {/* search */}
        <div className="relative mb-8">
          <div className="flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3.5 shadow-sm">
            <Search className="h-5 w-5 text-muted-foreground" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search person, phone, vehicle, location, case or transaction…"
              className="flex-1 bg-transparent text-base text-foreground placeholder:text-muted-foreground focus:outline-none"
            />
            {q && <button onClick={() => setQ("")} className="text-xs text-muted-foreground hover:text-foreground">Clear</button>}
          </div>
          {results.length > 0 && (
            <div className="absolute z-20 mt-1 w-full overflow-hidden rounded-xl border border-border bg-popover shadow-xl">
              {results.map((e) => (
                <Link
                  key={e.id}
                  to="/workspace"
                  onClick={() => selectEntity(e.id)}
                  className="flex items-center gap-3 border-b border-border/60 px-4 py-2.5 last:border-0 hover:bg-accent"
                >
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: `hsl(${entityColor(e.type)})` }} />
                  <div className="flex-1">
                    <p className="text-sm text-foreground">{e.name}</p>
                    <p className="text-[11px] text-muted-foreground">{ENTITY_META[e.type].label}{e.role ? ` · ${e.role}` : ""}</p>
                  </div>
                  <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* metrics */}
        <div className="mb-8 grid grid-cols-2 gap-3 lg:grid-cols-4">
          <Metric icon={FolderArchive} label="Active investigations" value={INVESTIGATIONS.filter((i) => i.status === "active").length} />
          <Metric icon={Lightbulb} label="Pending leads" value={LEADS.filter((l) => l.status === "new" || l.status === "reviewing").length} />
          <Metric icon={ShieldCheck} label="Evidence reviewed" value={EVIDENCE.length} />
          <Metric icon={Network} label="Network anomalies" value={LEADS.filter((l) => !l.documented).length} />
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          {/* pinned investigations */}
          <div className="rounded-xl border border-border bg-card p-5">
            <div className="mb-3 flex items-center gap-2">
              <Pin className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold text-foreground">Pinned investigations</h2>
            </div>
            <div className="space-y-2">
              {recentInvestigations.map((inv) => (
                <Link key={inv.id} to="/workspace" onClick={() => setCurrentInvestigationId(inv.id)} className="block rounded-lg border border-border bg-background p-3 transition hover:border-primary/40 hover:bg-accent">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-foreground">{inv.title}</p>
                    <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
                  </div>
                  <p className="mt-0.5 text-[11px] text-muted-foreground">{inv.caseRef} · {inv.status}</p>
                </Link>
              ))}
              {INVESTIGATIONS.filter((i) => !pinned.includes(i.id)).map((inv) => (
                <Link key={inv.id} to="/workspace" onClick={() => setCurrentInvestigationId(inv.id)} className="block rounded-lg border border-dashed border-border p-3 transition hover:border-primary/40 hover:bg-accent">
                  <p className="text-sm text-foreground">{inv.title}</p>
                  <p className="mt-0.5 text-[11px] text-muted-foreground">{inv.summary.slice(0, 60)}…</p>
                </Link>
              ))}
            </div>
          </div>

          {/* recent entities + saved leads */}
          <div className="rounded-xl border border-border bg-card p-5">
            <h2 className="mb-3 text-sm font-semibold text-foreground">Recently viewed</h2>
            <div className="space-y-1.5">
              {recentEntities.map((e) => (
                <Link key={e.id} to="/workspace" onClick={() => selectEntity(e.id)} className="flex items-center gap-2.5 rounded-md px-2 py-1.5 transition hover:bg-accent">
                  <span className="h-2 w-2 rounded-full" style={{ background: `hsl(${entityColor(e.type)})` }} />
                  <span className="flex-1 truncate text-sm text-foreground">{e.name}</span>
                  <span className="text-[10px] text-muted-foreground">{ENTITY_META[e.type].label}</span>
                </Link>
              ))}
            </div>
            <h2 className="mb-2 mt-5 text-sm font-semibold text-foreground">Saved leads</h2>
            <div className="space-y-1.5">
              {savedLeadObjs.map((l) => (
                <div key={l.id} className="flex items-center gap-2 rounded-md px-2 py-1.5">
                  {l.documented ? <ShieldCheck className="h-3.5 w-3.5 text-primary" /> : <Sparkles className="h-3.5 w-3.5 text-muted-foreground" />}
                  <span className="flex-1 truncate text-xs text-foreground">{l.title}</span>
                </div>
              ))}
              {savedLeadObjs.length === 0 && <p className="text-xs text-muted-foreground">No saved leads yet.</p>}
            </div>
          </div>

          {/* activity timeline */}
          <div className="rounded-xl border border-border bg-card p-5">
            <div className="mb-3 flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold text-foreground">Activity timeline</h2>
            </div>
            <div className="space-y-3">
              {recentEvents.map((t) => (
                <div key={t.id} className="flex gap-2.5">
                  <Clock className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                  <div>
                    <p className="text-xs font-medium text-foreground">{t.title}</p>
                    <p className="text-[11px] text-muted-foreground">{t.date} · {t.kind}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* intelligence brief */}
        <div className="mt-5 rounded-xl border border-dashed border-primary/30 bg-primary/5 p-5">
          <div className="mb-1.5 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <h2 className="text-sm font-semibold text-foreground">Intelligence Brief</h2>
          </div>
          <p className="text-sm leading-relaxed text-foreground/85">
            Operation Monsoon shows a stable three-cluster structure: a core coordination group, a coastal logistics cluster, and an urban finance cluster.
            Two documented bridges (P1↔P2 communication, A1→A2 transfers) connect logistics and finance. The highest-confidence inferred lead (P1↔P3, 71%) warrants priority review.
          </p>
          <p className="mt-2 text-[11px] text-muted-foreground">AI-generated summary — verify against source evidence. DEMO.</p>
        </div>
      </div>
    </div>
  );
}

function Metric({ icon: Icon, label, value }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className="mb-2 flex items-center gap-2">
        <Icon className="h-4 w-4 text-muted-foreground" />
        <span className="text-[11px] uppercase tracking-wider text-muted-foreground">{label}</span>
      </div>
      <p className="text-2xl font-semibold text-foreground">{value}</p>
    </div>
  );
}