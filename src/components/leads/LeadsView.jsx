import React, { useState } from "react";
import { useApp } from "@/store/AppStore";
import { LEADS, ENTITIES, EVIDENCE } from "@/data/mockData";
import { entityColor, ENTITY_META } from "@/lib/graphUtils";
import { Sparkles, ShieldCheck, ChevronDown, ChevronUp, Bookmark, FileText, ArrowRight, X, Check, Pin } from "lucide-react";

const STATUS_STYLES = {
  new: "bg-sky-500/15 text-sky-400",
  reviewing: "bg-amber-500/15 text-amber-500",
  verified: "bg-emerald-500/15 text-emerald-500",
  dismissed: "bg-rose-500/15 text-rose-400",
  saved: "bg-violet-500/15 text-violet-400",
};

export default function LeadsView() {
  const { leads, updateLead, toggleSaveLead, savedLeads, selectEntity, openEvidence, pushToast } = useApp();
  const [expanded, setExpanded] = useState(new Set([leads[0]?.id]));
  const [filter, setFilter] = useState("all");

  const filtered = leads.filter((l) => filter === "all" || l.status === filter);

  const toggle = (id) => setExpanded((s) => {
    const n = new Set(s);
    if (n.has(id)) n.delete(id); else n.add(id);
    return n;
  });

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-border px-5 py-3">
        <div>
          <h2 className="text-sm font-semibold text-foreground">AI Lead Discovery</h2>
          <p className="text-[11px] text-muted-foreground">AI-generated summary — verify against source evidence. DEMO.</p>
        </div>
        <div className="flex gap-1">
          {["all", "new", "reviewing", "verified", "dismissed"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-md px-2.5 py-1 text-xs capitalize transition ${filter === f ? "bg-primary text-primary-foreground" : "border border-border text-muted-foreground hover:bg-accent"}`}
            >{f}</button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin p-5">
        <div className="mx-auto max-w-3xl space-y-3">
          {filtered.map((lead) => {
            const open = expanded.has(lead.id);
            return (
              <div key={lead.id} className="rounded-xl border border-border bg-card overflow-hidden">
                <div className="flex items-start gap-3 p-4">
                  <div className="mt-0.5">
                    {lead.documented ? <ShieldCheck className="h-4 w-4 text-primary" /> : <Sparkles className="h-4 w-4 text-muted-foreground" />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-medium text-foreground">{lead.title}</h3>
                      <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium capitalize ${STATUS_STYLES[lead.status]}`}>{lead.status}</span>
                    </div>
                    <div className="mt-1 flex flex-wrap items-center gap-1.5">
                      {lead.entities.map((eid) => {
                        const e = ENTITIES.find((x) => x.id === eid);
                        if (!e) return null;
                        return (
                          <button key={eid} onClick={() => selectEntity(eid)} className="flex items-center gap-1 rounded border border-border bg-accent px-1.5 py-0.5 text-[11px] transition hover:border-primary/40">
                            <span className="h-1.5 w-1.5 rounded-full" style={{ background: `hsl(${entityColor(e.type)})` }} />
                            {e.name}
                          </button>
                        );
                      })}
                      {!lead.documented && (
                        <span className="ml-auto text-[11px] text-muted-foreground">Confidence <span className="font-medium text-foreground">{Math.round(lead.confidence * 100)}%</span></span>
                      )}
                    </div>
                  </div>
                  <button onClick={() => toggle(lead.id)} className="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground">
                    {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </button>
                </div>

                {open && (
                  <div className="border-t border-border bg-muted/20 p-4">
                    <div className="mb-3">
                      <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Why this lead?</p>
                      <ul className="space-y-1.5">
                        {lead.why.map((w, i) => (
                          <li key={i} className="flex gap-2 text-xs text-foreground/85">
                            <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary" />
                            {w}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {lead.evidence.length > 0 && (
                      <div className="mb-3">
                        <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Supporting evidence</p>
                        <div className="flex flex-wrap gap-1.5">
                          {lead.evidence.map((eid) => {
                            const ev = EVIDENCE.find((x) => x.id === eid);
                            if (!ev) return null;
                            return (
                              <button key={eid} onClick={() => openEvidence(eid)} className="flex items-center gap-1.5 rounded-md border border-border bg-card px-2 py-1 text-[11px] transition hover:border-primary/40">
                                <FileText className="h-3 w-3 text-muted-foreground" /> {ev.ref}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    <div className="mb-3 rounded-md border border-border bg-card p-2.5">
                      <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Suggested next step</p>
                      <p className="mt-1 text-xs text-foreground/85">{lead.nextStep}</p>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <ActionBtn onClick={() => { toggleSaveLead(lead.id); pushToast(savedLeads.includes(lead.id) ? "Lead unsaved" : "Lead saved"); }}>
                        <Bookmark className={`h-3.5 w-3.5 ${savedLeads.includes(lead.id) ? "fill-primary text-primary" : ""}`} /> {savedLeads.includes(lead.id) ? "Saved" : "Save lead"}
                      </ActionBtn>
                      <ActionBtn onClick={() => updateLead(lead.id, "reviewing")}><Check className="h-3.5 w-3.5" /> Mark reviewing</ActionBtn>
                      <ActionBtn onClick={() => updateLead(lead.id, "verified")}><ShieldCheck className="h-3.5 w-3.5" /> Verify</ActionBtn>
                      <ActionBtn onClick={() => updateLead(lead.id, "dismissed")}><X className="h-3.5 w-3.5" /> Dismiss</ActionBtn>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          {filtered.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Sparkles className="mb-2 h-8 w-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">No leads match this filter.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ActionBtn({ children, onClick }) {
  return (
    <button onClick={onClick} className="flex items-center gap-1.5 rounded-md border border-border bg-card px-2.5 py-1.5 text-xs font-medium text-foreground transition hover:bg-accent">
      {children}
    </button>
  );
}