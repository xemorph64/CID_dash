import React, { useMemo, useState } from "react";
import { useApp } from "@/store/AppStore";
import { ENTITIES, RELATIONSHIPS } from "@/data/mockData";
import { disruptionMetrics, entityColor, ENTITY_META } from "@/lib/graphUtils";
import { Crosshair, RotateCcw, Play, AlertTriangle, Network } from "lucide-react";

export default function DisruptionSimulator() {
  const { disruptionSelection, setDisruptionSelection, selectEntity, pushToast } = useApp();
  const [simulated, setSimulated] = useState(false);

  const original = useMemo(() => disruptionMetrics(ENTITIES, RELATIONSHIPS, []), []);
  const after = useMemo(() => disruptionMetrics(ENTITIES, RELATIONSHIPS, disruptionSelection), [disruptionSelection]);

  const toggleEntity = (id) => {
    setDisruptionSelection((s) => s.includes(id) ? s.filter((x) => x !== id) : [...s, id]);
    setSimulated(false);
  };

  const reset = () => { setDisruptionSelection([]); setSimulated(false); pushToast("Simulation reset"); };

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border px-5 py-3">
        <div className="flex items-center gap-2">
          <Crosshair className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Network Disruption Simulator</h2>
          <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-[10px] font-medium text-amber-500">HYPOTHETICAL</span>
        </div>
        <p className="mt-1 text-[11px] text-muted-foreground">Explore the hypothetical impact of removing entities. Not a prediction of real events. DEMO.</p>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* selection */}
        <div className="w-72 shrink-0 overflow-y-auto scrollbar-thin border-r border-border p-4">
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Select entities to remove ({disruptionSelection.length})</p>
          <div className="space-y-1">
            {ENTITIES.filter((e) => e.type === "person" || e.type === "organization").map((e) => {
              const sel = disruptionSelection.includes(e.id);
              return (
                <button
                  key={e.id}
                  onClick={() => toggleEntity(e.id)}
                  className={`flex w-full items-center gap-2 rounded-md border px-2.5 py-1.5 text-left text-xs transition ${sel ? "border-rose-500/50 bg-rose-500/10" : "border-border bg-card hover:bg-accent"}`}
                >
                  <span className="h-2 w-2 rounded-full" style={{ background: `hsl(${entityColor(e.type)})` }} />
                  <span className="flex-1 truncate text-foreground">{e.name}</span>
                  {sel && <span className="text-[10px] text-rose-400">removed</span>}
                </button>
              );
            })}
          </div>
        </div>

        {/* metrics */}
        <div className="flex-1 overflow-y-auto scrollbar-thin p-5">
          <div className="mb-4 flex items-center gap-2">
            <button
              onClick={() => { setSimulated(true); pushToast("Disruption simulated"); }}
              disabled={disruptionSelection.length === 0}
              className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground transition hover:opacity-90 disabled:opacity-40"
            >
              <Play className="h-3.5 w-3.5" /> Simulate removal
            </button>
            <button onClick={reset} className="flex items-center gap-1.5 rounded-md border border-border bg-card px-3 py-1.5 text-xs font-medium text-foreground transition hover:bg-accent">
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <Metric label="Entities removed" before={0} after={after.removedEntities} />
            <Metric label="Remaining entities" before={original.remainingEntities} after={after.remainingEntities} />
            <Metric label="Affected relationships" before={0} after={after.affectedRelationships} />
            <Metric label="Remaining relationships" before={original.remainingRelationships} after={after.remainingRelationships} />
            <Metric label="Connected components" before={original.connectedComponents} after={after.connectedComponents} highlight={after.connectedComponents > original.connectedComponents} />
            <Metric label="Largest component size" before={original.largestComponent} after={after.largestComponent} />
            <Metric label="Disconnected clusters" before={original.disconnectedClusters} after={after.disconnectedClusters} highlight={after.disconnectedClusters > original.disconnectedClusters} />
            <Metric label="Original components" before={original.originalComponents} after={original.originalComponents} />
          </div>

          {simulated && disruptionSelection.length > 0 && (
            <div className="mt-5 rounded-lg border border-amber-500/30 bg-amber-500/5 p-4">
              <div className="mb-1.5 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-500" />
                <p className="text-sm font-medium text-foreground">Impact summary</p>
              </div>
              <p className="text-xs leading-relaxed text-foreground/85">
                Removing {after.removedEntities} {after.removedEntities === 1 ? "entity" : "entities"} would affect {after.affectedRelationships} relationships.
                {after.connectedComponents > original.connectedComponents
                  ? ` The network would fragment into ${after.connectedComponents} separate clusters (up from ${original.connectedComponents}), suggesting these entities act as bridges between groups.`
                  : after.affectedRelationships > 0
                    ? " The network would remain connected but with reduced redundancy."
                    : " No measurable structural impact."}
              </p>
              <p className="mt-2 text-[11px] text-muted-foreground">This is a structural analysis of the demo graph, not a prediction of real-world outcomes.</p>
            </div>
          )}

          {!simulated && (
            <div className="mt-5 flex flex-col items-center justify-center py-12 text-center">
              <Network className="mb-2 h-8 w-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Select entities and run the simulation to compare before/after structure.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Metric({ label, before, after, highlight }) {
  const changed = after !== before;
  return (
    <div className={`rounded-lg border p-3 ${highlight ? "border-amber-500/40 bg-amber-500/5" : "border-border bg-card"}`}>
      <p className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</p>
      <div className="mt-1 flex items-baseline gap-2">
        <span className={`text-xl font-semibold ${changed ? "text-primary" : "text-foreground"}`}>{after}</span>
        {changed && <span className="text-[11px] text-muted-foreground line-through">{before}</span>}
      </div>
    </div>
  );
}