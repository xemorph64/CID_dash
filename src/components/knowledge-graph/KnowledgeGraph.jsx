import React, { useMemo, useRef, useState, useEffect, useCallback } from "react";
import { useApp } from "@/store/AppStore";
import { ENTITIES, RELATIONSHIPS } from "@/data/mockData";
import { computeLayout, entityColor, ENTITY_META, buildAdjacency, degree } from "@/lib/graphUtils";
import { ZoomIn, ZoomOut, Maximize, Crosshair, Eye, EyeOff } from "lucide-react";

const WIDTH = 1180;
const HEIGHT = 840;

export default function KnowledgeGraph() {
  const {
    selectedEntityId, selectEntity, selectedRelationshipId, selectRelationship,
    focusEntityId, setFocusEntityId, activeLayer, openEvidenceForRelationship,
    highlightPath, timelineDate,
  } = useApp();

  const svgRef = useRef(null);
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });
  const [hoverNode, setHoverNode] = useState(null);
  const [showLabels, setShowLabels] = useState(true);
  const [dragging, setDragging] = useState(null);

  const positions = useMemo(() => computeLayout(ENTITIES, RELATIONSHIPS, WIDTH, HEIGHT), []);
  const adj = useMemo(() => buildAdjacency(ENTITIES, RELATIONSHIPS), []);

  // time filter: hide relationships whose observation window is entirely after the timeline date
  const visibleRelationships = useMemo(() => {
    return RELATIONSHIPS.filter((r) => {
      if (activeLayer !== "all" && r.category !== activeLayer && r.category !== "all") return false;
      if (timelineDate && r.first > timelineDate) return false;
      return true;
    });
  }, [activeLayer, timelineDate]);

  const visibleEntityIds = useMemo(() => {
    const ids = new Set();
    visibleRelationships.forEach((r) => { ids.add(r.source); ids.add(r.target); });
    // always show entities that exist by the timeline date via their first relationship
    return ids;
  }, [visibleRelationships]);

  const focusNeighbors = useMemo(() => {
    if (!focusEntityId) return null;
    const set = new Set([focusEntityId]);
    adj[focusEntityId]?.forEach((n) => set.add(n));
    return set;
  }, [focusEntityId, adj]);

  const pathEdges = useMemo(() => {
    if (!highlightPath) return new Set();
    const s = new Set();
    highlightPath.forEach((step) => {
      if (step.relationship) s.add(step.relationship.id);
    });
    return s;
  }, [highlightPath]);

  const pathNodes = useMemo(() => {
    if (!highlightPath) return new Set();
    const s = new Set();
    highlightPath.forEach((step) => { s.add(step.from); s.add(step.to); });
    return s;
  }, [highlightPath]);

  // pan/zoom handlers
  const onPointerDown = (e) => {
    if (e.target.tagName === "circle" || e.target.tagName === "text" || e.target.closest("[data-node]")) return;
    setDragging({ x: e.clientX, y: clientY(e), tx: transform.x, ty: transform.y });
  };
  const onPointerMove = (e) => {
    if (!dragging) return;
    setTransform((t) => ({ ...t, x: dragging.tx + (e.clientX - dragging.x), y: dragging.ty + (clientY(e) - dragging.y) }));
  };
  const onPointerUp = () => setDragging(null);

  const onWheel = useCallback((e) => {
    e.preventDefault();
    const delta = -e.deltaY * 0.0012;
    setTransform((t) => {
      const k = Math.min(2.6, Math.max(0.4, t.k + delta));
      return { ...t, k };
    });
  }, []);

  useEffect(() => {
    const el = svgRef.current;
    if (!el) return;
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, [onWheel]);

  const fit = () => setTransform({ x: 0, y: 0, k: 1 });
  const zoomBy = (d) => setTransform((t) => ({ ...t, k: Math.min(2.6, Math.max(0.4, t.k + d)) }));

  const isDimmed = (id) => {
    if (highlightPath && highlightPath.length) {
      return !pathNodes.has(id);
    }
    if (focusNeighbors) return !focusNeighbors.has(id);
    return false;
  };

  const edgeDimmed = (r) => {
    if (highlightPath && highlightPath.length) return !pathEdges.has(r.id);
    if (focusNeighbors) {
      return !(focusNeighbors.has(r.source) && focusNeighbors.has(r.target));
    }
    return false;
  };

  return (
    <div className="relative h-full w-full overflow-hidden rounded-xl border border-border bg-card grid-bg">
      {/* controls */}
      <div className="absolute right-3 top-3 z-20 flex flex-col gap-1.5">
        <GraphBtn onClick={() => zoomBy(0.2)} label="Zoom in"><ZoomIn className="h-4 w-4" /></GraphBtn>
        <GraphBtn onClick={() => zoomBy(-0.2)} label="Zoom out"><ZoomOut className="h-4 w-4" /></GraphBtn>
        <GraphBtn onClick={fit} label="Fit to screen"><Maximize className="h-4 w-4" /></GraphBtn>
        <GraphBtn onClick={() => setFocusEntityId(null)} active={!!focusEntityId} label="Exit focus"><Crosshair className="h-4 w-4" /></GraphBtn>
        <GraphBtn onClick={() => setShowLabels((v) => !v)} active={showLabels} label="Toggle labels">{showLabels ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}</GraphBtn>
      </div>

      {/* legend */}
      <div className="absolute left-3 top-3 z-20 rounded-lg border border-border bg-popover/90 px-3 py-2 text-[11px] backdrop-blur">
        <div className="mb-1 font-medium text-foreground/80">Relationships</div>
        <div className="flex items-center gap-2"><span className="inline-block h-0 w-6 border-t-2 border-primary" /> Documented (source-backed)</div>
        <div className="flex items-center gap-2"><span className="inline-block h-0 w-6 border-t-2 border-dashed border-muted-foreground" /> AI-inferred (hypothesis)</div>
        <div className="mt-1.5 text-muted-foreground">DEMO · simulated data</div>
      </div>

      <svg
        ref={svgRef}
        className="h-full w-full cursor-grab active:cursor-grabbing"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerLeave={onPointerUp}
      >
        <g transform={`translate(${transform.x},${transform.y}) scale(${transform.k})`}>
          {/* edges */}
          {visibleRelationships.map((r) => {
            const s = positions[r.source];
            const t = positions[r.target];
            if (!s || !t) return null;
            const selected = selectedRelationshipId === r.id;
            const dim = edgeDimmed(r);
            const onPath = pathEdges.has(r.id);
            const stroke = r.documented ? "hsl(var(--primary))" : "hsl(var(--muted-foreground))";
            return (
              <g key={r.id} className="cursor-pointer" onClick={() => selectRelationship(r.id)}>
                <line
                  x1={s.x} y1={s.y} x2={t.x} y2={t.y}
                  stroke={stroke}
                  strokeWidth={selected || onPath ? 3 : 1.6}
                  strokeDasharray={r.documented ? "none" : "6 5"}
                  opacity={dim ? 0.12 : selected || onPath ? 0.95 : 0.5}
                  className="transition-opacity"
                />
                {/* invisible wide hit area */}
                <line x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="transparent" strokeWidth={14} />
              </g>
            );
          })}

          {/* nodes */}
          {ENTITIES.filter((n) => visibleEntityIds.has(n.id)).map((n) => {
            const p = positions[n.id];
            if (!p) return null;
            const selected = selectedEntityId === n.id;
            const isFocus = focusEntityId === n.id;
            const dim = isDimmed(n.id);
            const onPath = pathNodes.has(n.id);
            const deg = degree(n.id, adj);
            const r = 8 + Math.min(deg, 6) * 1.4;
            const color = entityColor(n.type);
            return (
              <g
                key={n.id}
                data-node
                className="cursor-pointer"
                transform={`translate(${p.x},${p.y})`}
                onClick={() => selectEntity(n.id)}
                onDoubleClick={() => setFocusEntityId(n.id)}
                onMouseEnter={() => setHoverNode(n.id)}
                onMouseLeave={() => setHoverNode(null)}
                opacity={dim ? 0.18 : 1}
                style={{ transition: "opacity 0.25s" }}
              >
                {(selected || isFocus || onPath) && (
                  <circle r={r + 6} fill="none" stroke={color} strokeWidth={1.5} opacity={0.5} className="animate-pulse" />
                )}
                <circle r={r} fill={`hsl(${color})`} stroke="hsl(var(--background))" strokeWidth={2} />
                <circle r={r * 0.45} fill="hsl(var(--background))" opacity={0.85} />
                {showLabels && (
                  <text
                    y={r + 13}
                    textAnchor="middle"
                    className="pointer-events-none select-none"
                    fill="hsl(var(--foreground))"
                    fontSize={selected ? 12 : 10.5}
                    fontWeight={selected || isFocus ? 600 : 400}
                    opacity={dim ? 0.3 : 0.92}
                  >
                    {n.name.length > 22 ? n.name.slice(0, 20) + "…" : n.name}
                  </text>
                )}
              </g>
            );
          })}
        </g>
      </svg>

      {/* hover tooltip */}
      {hoverNode && (() => {
        const n = ENTITIES.find((e) => e.id === hoverNode);
        if (!n) return null;
        return (
          <div className="pointer-events-none absolute bottom-3 left-3 z-20 max-w-xs rounded-lg border border-border bg-popover/95 px-3 py-2 text-xs backdrop-blur">
            <div className="font-medium text-foreground">{n.name}</div>
            <div className="text-muted-foreground">{ENTITY_META[n.type]?.label}{n.role ? ` · ${n.role}` : ""}</div>
            <div className="mt-1 text-muted-foreground">{degree(n.id, adj)} connections · double-click to focus</div>
          </div>
        );
      })()}

      {/* minimap */}
      <Minimap positions={positions} visibleEntityIds={visibleEntityIds} transform={transform} />
    </div>
  );
}

function GraphBtn({ children, onClick, label, active }) {
  return (
    <button
      onClick={onClick}
      aria-label={label}
      title={label}
      className={`flex h-8 w-8 items-center justify-center rounded-md border border-border bg-popover/90 text-foreground/80 backdrop-blur transition hover:bg-accent hover:text-foreground ${active ? "ring-1 ring-primary text-primary" : ""}`}
    >
      {children}
    </button>
  );
}

function Minimap({ positions, visibleEntityIds, transform }) {
  const scale = 150 / WIDTH;
  return (
    <div className="absolute bottom-3 right-3 z-20 rounded-md border border-border bg-popover/80 p-1 backdrop-blur">
      <svg width={150} height={Math.round(HEIGHT * scale)} className="block">
        <g transform={`scale(${scale})`}>
          {Object.entries(positions).map(([id, p]) => (
            <circle key={id} cx={p.x} cy={p.y} r={3} fill={visibleEntityIds.has(id) ? "hsl(var(--primary))" : "hsl(var(--muted-foreground) / 0.4)"} />
          ))}
        </g>
        <rect
          x={Math.max(0, -transform.x / transform.k) * scale}
          y={Math.max(0, -transform.y / transform.k) * scale}
          width={Math.min(WIDTH, (WIDTH / transform.k)) * scale}
          height={Math.min(HEIGHT, (HEIGHT / transform.k)) * scale}
          fill="none"
          stroke="hsl(var(--foreground))"
          strokeWidth={1}
          opacity={0.5}
        />
      </svg>
    </div>
  );
}

function clientY(e) { return e.clientY; }