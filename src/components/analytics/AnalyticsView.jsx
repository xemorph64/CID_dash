import React, { useMemo } from "react";
import { useApp } from "@/store/AppStore";
import { ENTITIES, RELATIONSHIPS, TIMELINE_EVENTS } from "@/data/mockData";
import { buildAdjacency, degree, entityColor, ENTITY_META } from "@/lib/graphUtils";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, CartesianGrid, Legend } from "recharts";

const PIE_COLORS = ["hsl(var(--c-person))", "hsl(var(--c-phone))", "hsl(var(--c-vehicle))", "hsl(var(--c-location))", "hsl(var(--c-organization))", "hsl(var(--c-case))", "hsl(var(--c-account))", "hsl(var(--c-event))"];

export default function AnalyticsView() {
  const adj = useMemo(() => buildAdjacency(ENTITIES, RELATIONSHIPS), []);

  const mostConnected = useMemo(() => {
    return [...ENTITIES].map((e) => ({ ...e, deg: degree(e.id, adj) })).sort((a, b) => b.deg - a.deg).slice(0, 8);
  }, [adj]);

  const typeDistribution = useMemo(() => {
    const counts = {};
    ENTITIES.forEach((e) => { counts[e.type] = (counts[e.type] || 0) + 1; });
    return Object.entries(counts).map(([type, count]) => ({ type, count, label: ENTITY_META[type].label }));
  }, []);

  const relDistribution = useMemo(() => {
    const counts = {};
    RELATIONSHIPS.forEach((r) => { counts[r.type] = (counts[r.type] || 0) + 1; });
    return Object.entries(counts).map(([type, count]) => ({ type, count })).sort((a, b) => b.count - a.count);
  }, []);

  const activityOverTime = useMemo(() => {
    const byMonth = {};
    TIMELINE_EVENTS.forEach((t) => {
      const m = t.date.slice(0, 7);
      byMonth[m] = byMonth[m] || { month: m, communication: 0, financial: 0, case: 0, movement: 0 };
      byMonth[m][t.kind]++;
    });
    return Object.values(byMonth).sort((a, b) => a.month.localeCompare(b.month));
  }, []);

  const documentedCount = RELATIONSHIPS.filter((r) => r.documented).length;

  return (
    <div className="flex h-full flex-col overflow-y-auto scrollbar-thin">
      <div className="border-b border-border px-5 py-3">
        <h2 className="text-sm font-semibold text-foreground">Network Analytics</h2>
        <p className="text-[11px] text-muted-foreground">Structural metrics computed from the demo graph. All figures are simulated.</p>
      </div>

      <div className="grid grid-cols-2 gap-3 p-5 lg:grid-cols-4">
        <KPI label="Total entities" value={ENTITIES.length} />
        <KPI label="Total relationships" value={RELATIONSHIPS.length} />
        <KPI label="Documented" value={documentedCount} />
        <KPI label="AI-inferred" value={RELATIONSHIPS.length - documentedCount} />
      </div>

      <div className="grid gap-4 px-5 pb-5 lg:grid-cols-2">
        <ChartCard title="Most connected entities" explanation="Entities ranked by number of direct relationships. Useful for spotting central figures.">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={mostConnected.map((e) => ({ name: e.name.split(" ").slice(-1)[0], connections: e.deg }))} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={11} />
              <YAxis type="category" dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={11} width={70} />
              <Tooltip contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="connections" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Entity type distribution" explanation="Composition of the network by entity category.">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={typeDistribution} dataKey="count" nameKey="label" cx="50%" cy="50%" outerRadius={90} innerRadius={45} paddingAngle={2}>
                {typeDistribution.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Relationship types" explanation="How connections are distributed across relationship categories.">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={relDistribution} margin={{ left: 10, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="type" stroke="hsl(var(--muted-foreground))" fontSize={10} angle={-35} textAnchor="end" height={60} interval={0} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} />
              <Tooltip contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="count" fill="hsl(var(--c-account))" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Activity over time" explanation="Timeline events by kind across the observation window.">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={activityOverTime} margin={{ left: -10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={11} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} allowDecimals={false} />
              <Tooltip contentStyle={{ background: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Line type="monotone" dataKey="communication" stroke="hsl(var(--c-phone))" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="financial" stroke="hsl(var(--c-account))" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="case" stroke="hsl(var(--c-case))" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="movement" stroke="hsl(var(--c-location))" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}

function KPI({ label, value }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-[11px] uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-foreground">{value}</p>
    </div>
  );
}

function ChartCard({ title, explanation, children }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <h3 className="text-sm font-medium text-foreground">{title}</h3>
      <p className="mb-3 text-[11px] text-muted-foreground">{explanation}</p>
      {children}
    </div>
  );
}