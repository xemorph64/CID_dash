import React, { useState, useEffect, useRef } from "react";
import { useApp } from "@/store/AppStore";
import { INVESTIGATIONS, ENTITIES, EVIDENCE } from "@/data/mockData";
import { Search, ArrowRight, FolderArchive, Users, FileText, Lightbulb, Crosshair, Sun, Moon, Network, CornerDownLeft } from "lucide-react";

export default function CommandPalette() {
  const { commandPaletteOpen, setCommandPaletteOpen, setCurrentInvestigationId, setTheme, theme, pushToast, selectEntity, openEvidence } = useApp();
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const inputRef = useRef(null);

  useEffect(() => {
    if (commandPaletteOpen) {
      setQuery("");
      setActive(0);
      setTimeout(() => inputRef.current?.focus(), 30);
    }
  }, [commandPaletteOpen]);

  const commands = [
    ...INVESTIGATIONS.map((i) => ({ id: `inv-${i.id}`, label: `Open investigation: ${i.title}`, icon: FolderArchive, run: () => { setCurrentInvestigationId(i.id); pushToast(`Opened ${i.title}`); } })),
    { id: "cmd-find-entity", label: "Find entity", icon: Users, run: () => pushToast("Use the search below to find an entity") },
    { id: "cmd-search-evidence", label: "Search evidence", icon: FileText, run: () => pushToast("Select an evidence item below") },
    { id: "cmd-leads", label: "View saved leads", icon: Lightbulb, run: () => pushToast("Opening leads…") },
    { id: "cmd-disruption", label: "Open disruption simulator", icon: Crosshair, run: () => pushToast("Open Disruption Analysis from the navigator") },
    { id: "cmd-theme", label: "Switch theme", icon: theme === "dark" ? Sun : Moon, run: () => setTheme(theme === "dark" ? "light" : "dark") },
  ];

  const entityResults = query
    ? ENTITIES.filter((e) => e.name.toLowerCase().includes(query.toLowerCase())).slice(0, 6)
    : [];
  const evidenceResults = query
    ? EVIDENCE.filter((e) => e.ref.toLowerCase().includes(query.toLowerCase()) || e.title.toLowerCase().includes(query.toLowerCase())).slice(0, 4)
    : [];
  const commandResults = query
    ? commands.filter((c) => c.label.toLowerCase().includes(query.toLowerCase()))
    : commands;

  const flat = [
    ...commandResults.map((c) => ({ type: "command", ...c })),
    ...entityResults.map((e) => ({ type: "entity", id: `ent-${e.id}`, label: e.name, sub: e.type, entity: e, icon: Users, run: () => { selectEntity(e.id); pushToast(`Selected ${e.name}`); } })),
    ...evidenceResults.map((e) => ({ type: "evidence", id: `ev-${e.id}`, label: e.ref, sub: e.title, icon: FileText, run: () => { openEvidence(e.id); pushToast(`Opened ${e.ref}`); } })),
  ];

  if (!commandPaletteOpen) return null;

  const onKeyDown = (e) => {
    if (e.key === "ArrowDown") { e.preventDefault(); setActive((a) => Math.min(flat.length - 1, a + 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive((a) => Math.max(0, a - 1)); }
    else if (e.key === "Enter") { e.preventDefault(); flat[active]?.run(); setCommandPaletteOpen(false); }
    else if (e.key === "Escape") { setCommandPaletteOpen(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-background/60 backdrop-blur-sm" onClick={() => setCommandPaletteOpen(false)}>
      <div className="mt-[12vh] w-full max-w-xl overflow-hidden rounded-xl border border-border bg-popover shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center gap-2 border-b border-border px-4 py-3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => { setQuery(e.target.value); setActive(0); }}
            onKeyDown={onKeyDown}
            placeholder="Search entities, evidence, or run a command…"
            className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
          />
          <kbd className="rounded border border-border bg-background px-1.5 py-0.5 text-[10px] text-muted-foreground">ESC</kbd>
        </div>
        <div className="max-h-[50vh] overflow-y-auto scrollbar-thin p-2">
          {flat.length === 0 && <p className="px-3 py-6 text-center text-sm text-muted-foreground">No results.</p>}
          {flat.map((item, i) => {
            const Icon = item.icon || Search;
            return (
              <button
                key={item.id}
                onMouseEnter={() => setActive(i)}
                onClick={() => { item.run(); setCommandPaletteOpen(false); }}
                className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-left transition ${active === i ? "bg-accent" : "hover:bg-accent/50"}`}
              >
                <Icon className="h-4 w-4 shrink-0 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm text-foreground">{item.label}</p>
                  {item.sub && <p className="truncate text-[11px] capitalize text-muted-foreground">{item.sub}</p>}
                </div>
                {item.type === "entity" && <span className="text-[10px] text-muted-foreground">entity</span>}
                {active === i && <CornerDownLeft className="h-3.5 w-3.5 text-muted-foreground" />}
              </button>
            );
          })}
        </div>
        <div className="flex items-center justify-between border-t border-border px-4 py-2 text-[10px] text-muted-foreground">
          <span>↑↓ navigate · ↵ select · esc close</span>
          <span>DEMO · C.I.D.</span>
        </div>
      </div>
    </div>
  );
}