import React from "react";
import { Link } from "react-router-dom";
import { useApp } from "@/store/AppStore";
import { INVESTIGATIONS } from "@/data/mockData";
import { ShieldCheck, ArrowRight, Activity, Database, Network, AlertTriangle } from "lucide-react";

export default function Welcome() {
  const { setCurrentInvestigationId } = useApp();
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-4">
      <div className="absolute inset-0 grid-bg opacity-40" />
      <div className="absolute left-1/2 top-1/2 h-[36rem] w-[36rem] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 blur-[120px]" />

      <div className="relative z-10 w-full max-w-2xl text-center">
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg">
          <ShieldCheck className="h-8 w-8" />
        </div>
        <h1 className="text-4xl font-semibold tracking-tight text-foreground sm:text-5xl">C.I.D.</h1>
        <p className="mt-2 text-sm font-medium uppercase tracking-[0.3em] text-muted-foreground">Criminal Intelligence &amp; Disruption</p>

        <p className="mx-auto mt-6 max-w-xl text-balance text-base leading-relaxed text-muted-foreground">
          An AI-assisted analysis environment for mapping criminal networks, tracing evidence to its source,
          and distinguishing documented fact from analytical hypothesis.
        </p>

        <div className="mt-8 flex flex-col items-center gap-3">
          <Link
            to="/workspace"
            onClick={() => setCurrentInvestigationId("inv-monsoon")}
            className="group flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground transition hover:opacity-90"
          >
            Enter Investigation Workspace
            <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
          </Link>
          <Link to="/command-center" className="text-sm text-muted-foreground transition hover:text-foreground">
            or open the Command Center
          </Link>
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-2">
          <Badge icon={Activity} label="Demo environment" tone="amber" />
          <Badge icon={Database} label="Simulated data" />
          <Badge icon={Network} label="No live systems" />
        </div>

        <div className="mt-10 grid grid-cols-3 gap-3 text-left">
          <SampleCard title="Operation Monsoon" desc="Interconnected smuggling & finance network" onClick={() => setCurrentInvestigationId("inv-monsoon")} />
          <SampleCard title="Harbor Ledger" desc="Financial-flow follow-up" onClick={() => setCurrentInvestigationId("inv-harbor")} />
          <SampleCard title="Orchid Realty Probe" desc="Shell-ownership patterns" onClick={() => setCurrentInvestigationId("inv-orchid")} />
        </div>

        <p className="mt-8 flex items-center justify-center gap-1.5 text-[11px] text-muted-foreground">
          <AlertTriangle className="h-3 w-3" /> All entities, records, and leads are fictional. Not connected to any real system.
        </p>
      </div>
    </div>
  );
}

function Badge({ icon: Icon, label, tone }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs ${tone === "amber" ? "border-amber-500/30 bg-amber-500/10 text-amber-500" : "border-border bg-card text-muted-foreground"}`}>
      <Icon className="h-3 w-3" /> {label}
    </span>
  );
}

function SampleCard({ title, desc, onClick }) {
  return (
    <Link to="/workspace" onClick={onClick} className="block rounded-lg border border-border bg-card/70 p-3 transition hover:border-primary/40 hover:bg-accent">
      <p className="text-sm font-medium text-foreground">{title}</p>
      <p className="mt-0.5 text-[11px] text-muted-foreground">{desc}</p>
    </Link>
  );
}