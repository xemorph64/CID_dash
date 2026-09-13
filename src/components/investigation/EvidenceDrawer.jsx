import React, { useState } from "react";
import { useApp } from "@/store/AppStore";
import { EVIDENCE } from "@/data/mockData";
import { FileText, X, Bookmark, StickyNote, ArrowLeft, ShieldCheck, Sparkles } from "lucide-react";

const KIND_COLOR = {
  FIR: "var(--c-case)",
  CDR: "var(--c-phone)",
  TXN: "var(--c-account)",
  VEH: "var(--c-vehicle)",
  INT: "var(--c-event)",
};

export default function EvidenceDrawer() {
  const { evidenceDrawerOpen, setEvidenceDrawerOpen, evidenceItems, addNote, notes, pushToast } = useApp();
  const [activeId, setActiveId] = useState(null);
  const [bookmarks, setBookmarks] = useState(new Set());
  const [noteText, setNoteText] = useState("");

  if (!evidenceDrawerOpen) return null;
  const active = evidenceItems.find((e) => e.id === activeId) || evidenceItems[0];
  const activeNotes = active ? notes.filter((n) => n.scope === `evidence:${active.id}`) : [];

  const toggleBookmark = (id) => {
    setBookmarks((b) => {
      const next = new Set(b);
      if (next.has(id)) { next.delete(id); pushToast("Removed bookmark"); }
      else { next.add(id); pushToast("Evidence bookmarked"); }
      return next;
    });
  };

  return (
    <div className="absolute inset-x-0 bottom-0 z-30 h-[42%] border-t border-border bg-card shadow-2xl">
      <div className="flex h-full">
        {/* list */}
        <div className="w-64 shrink-0 overflow-y-auto scrollbar-thin border-r border-border">
          <div className="sticky top-0 flex items-center justify-between border-b border-border bg-card px-3 py-2.5">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Evidence ({evidenceItems.length})</span>
            <button onClick={() => setEvidenceDrawerOpen(false)} className="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground"><X className="h-4 w-4" /></button>
          </div>
          {evidenceItems.length === 0 ? (
            <p className="p-4 text-xs text-muted-foreground">No evidence items.</p>
          ) : evidenceItems.map((e) => (
            <button
              key={e.id}
              onClick={() => setActiveId(e.id)}
              className={`flex w-full items-start gap-2 border-b border-border/60 px-3 py-2.5 text-left transition ${active?.id === e.id ? "bg-accent" : "hover:bg-accent/50"}`}
            >
              <span className="mt-0.5 shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold" style={{ background: `hsl(${KIND_COLOR[e.kind]} / 0.15)`, color: `hsl(${KIND_COLOR[e.kind]})` }}>{e.kind}</span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-medium text-foreground">{e.ref}</p>
                <p className="truncate text-[11px] text-muted-foreground">{e.title}</p>
              </div>
              {bookmarks.has(e.id) && <Bookmark className="h-3.5 w-3.5 shrink-0 fill-primary text-primary" />}
            </button>
          ))}
        </div>

        {/* detail */}
        <div className="flex-1 overflow-y-auto scrollbar-thin p-5">
          {active ? (
            <div>
              <div className="mb-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="rounded px-2 py-0.5 text-[11px] font-bold" style={{ background: `hsl(${KIND_COLOR[active.kind]} / 0.15)`, color: `hsl(${KIND_COLOR[active.kind]})` }}>{active.kind}</span>
                  <h3 className="text-sm font-semibold text-foreground">{active.ref}</h3>
                  {active.status === "documented" ? (
                    <span className="inline-flex items-center gap-1 text-[11px] text-primary"><ShieldCheck className="h-3 w-3" /> Source-backed</span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground"><Sparkles className="h-3 w-3" /> Inferred support</span>
                  )}
                </div>
                <button onClick={() => toggleBookmark(active.id)} className="flex items-center gap-1.5 rounded-md border border-border bg-accent px-2.5 py-1.5 text-xs font-medium text-foreground transition hover:bg-secondary">
                  <Bookmark className={`h-3.5 w-3.5 ${bookmarks.has(active.id) ? "fill-primary text-primary" : ""}`} /> {bookmarks.has(active.id) ? "Bookmarked" : "Bookmark"}
                </button>
              </div>

              <div className="mb-4 grid grid-cols-3 gap-3 text-xs">
                <Meta label="Date" value={active.date} />
                <Meta label="Reference" value={active.ref} />
                <Meta label="Type" value={active.kind} />
              </div>

              <h4 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Source excerpt</h4>
              <div className="rounded-lg border border-border bg-muted/30 p-4 text-sm leading-relaxed text-foreground/90">
                {active.excerpt}
              </div>
              <p className="mt-2 text-[11px] text-muted-foreground">DEMO · simulated record. No real personal data.</p>

              <h4 className="mb-2 mt-5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Investigator notes</h4>
              <div className="mb-2 flex gap-1.5">
                <input
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && noteText.trim()) { addNote(`evidence:${active.id}`, noteText.trim()); setNoteText(""); } }}
                  placeholder="Attach a note to this evidence…"
                  className="flex-1 rounded-md border border-input bg-background px-2.5 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                />
                <button onClick={() => { if (noteText.trim()) { addNote(`evidence:${active.id}`, noteText.trim()); setNoteText(""); } }} className="rounded-md border border-border bg-accent px-3 py-1.5 text-xs font-medium text-foreground transition hover:bg-secondary">Add</button>
              </div>
              <div className="space-y-1.5">
                {activeNotes.map((n) => (
                  <div key={n.id} className="rounded-md border border-border bg-muted/30 p-2 text-xs">
                    <p className="text-foreground">{n.text}</p>
                    <p className="mt-1 text-[10px] text-muted-foreground">{n.author} · {new Date(n.ts).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Select an evidence item.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function Meta({ label, value }) {
  return (
    <div className="rounded-md border border-border bg-card p-2.5">
      <p className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className="mt-0.5 text-sm font-medium text-foreground">{value}</p>
    </div>
  );
}