import React, { useMemo, useState } from "react";
import { useApp } from "@/store/AppStore";
import { ENTITIES, RELATIONSHIPS } from "@/data/mockData";
import { findPaths, entityColor, ENTITY_META } from "@/lib/graphUtils";
import { ArrowRight, Route, ShieldCheck, Sparkles, Search } from "lucide-react";

export default function PathExplorer() {
  const { pathSource, setPathSource, pathTarget, setPathTarget, setHighlightPath, selectEntity, pushToast } = useApp();
  const [results, setResults] = useState([]);

  const run = () => {
    if (!pathSource || !pathTarget || pathSource === pathTarget) {
      pushToast("Select two different entities");
      return;
    }
    const paths = findPaths(ENTITIES, RELATIONSHIPS, pathSource, pathTarget, 5, 6);
    setResults(paths);
    if (paths.length) { setHighlightPath(paths[0]); pushToast(`${paths.length} path${paths.length > 1 ? "s" : ""} found`); }
    else { setHighlightPath(null); pushToast("No path found within depth limit"); }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border px-5 py-3">
        <div className="flex items-center gap-2">
          <Route className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Investigation Path Explorer</h2>
        </div>
        <p className="mt-1 text-[11px] text-muted-foreground">Trace possible connections between two entities through the network. DEMO.</p>
      </div>

      <div className="border-b border-border p-4">
        <div className="flex flex-wrap items-end gap-3">
          <EntitySelect label="From" value={pathSource} onChange={setPathSource} />
          <ArrowRight className="mb-2 h-4 w-4 text-muted-foreground" />
          <EntitySelect label="To" value={pathTarget} onChange={setPathTarget} />
          <button onClick={run} className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-2 text-xs font-medium text-primary-foreground transition hover:opacity-90">
            <Search className="h-3.5 w-3.5" /> Find paths
          </button>
          <button onClick={() => { setResults([]); setHighlightPath(null); setPathSource(null); setPathTarget(null); }} className="rounded-md border border-border bg-card px-3 py-2 text-xs font-medium text-foreground transition hover:bg-accent">Clear</button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin p-5">
        {results.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <Route className="mb-2 h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Select a starting and destination entity, then find paths.</p>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-3">
            {results.map((path, i) => (
              <button
                key={i}
                onClick={() => setHighlightPath(path)}
                className={`block w-full rounded-xl border p-4 text-left transition ${i === 0 ? "border-primary/40 bg-primary/5" : "border-border bg-card hover:bg-accent"}`}
              >
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-medium text-foreground">Path {i + 1} · {path.length} {path.length === 1 ? "hop" : "hops"}</span>
                  <span className="text-[11px] text-muted-foreground">{path.filter(s => s.relationship?.documented).length}/{path.length} documented</span>
                </div>
                <div className="flex flex-wrap items-center gap-1.5">
                  {path.map((step, j) => {
                    const from = ENTITIES.find((e) => e.id === step.from);
                    const to = ENTITIES.find((e) => e.id === step.to);
                    return (
                      <React.Fragment key={j}>
                        <span className="flex items-center gap-1 rounded border border-border bg-accent px-1.5 py-0.5 text-[11px]">
                          <span className="h-1.5 w-1.5 rounded-full" style={{ background: `hsl(${entityColor(from.type)})` }} />
                          {from.name}
                        </span>
                        <span className="flex items-center gap-1 text-muted-foreground">
                          {step.relationship?.documented ? <ShieldCheck className="h-3 w-3 text-primary" /> : <Sparkles className="h-3 w-3" />}
                          <ArrowRight className="h-3 w-3" />
                        </span>
                        {j === path.length - 1 && (
                          <span className="flex items-center gap-1 rounded border border-border bg-accent px-1.5 py-0.5 text-[11px]">
                            <span className="h-1.5 w-1.5 rounded-full" style={{ background: `hsl(${entityColor(to.type)})` }} />
                            {to.name}
                          </span>
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {path.map((step, j) => (
                    <span key={j} className="rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">{step.relationship?.type}</span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function EntitySelect({ label, value, onChange }) {
  return (
    <div>
      <label className="mb-1 block text-[11px] font-medium uppercase tracking-wider text-muted-foreground">{label}</label>
      <select value={value || ""} onChange={(e) => onChange(e.target.value || null)} className="min-w-[12rem] rounded-md border border-input bg-background px-2.5 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring">
        <option value="">Select entity…</option>
        {ENTITIES.map((e) => (
          <option key={e.id} value={e.id}>{e.name} ({ENTITY_META[e.type].label})</option>
        ))}
      </select>
    </div>
  );
}