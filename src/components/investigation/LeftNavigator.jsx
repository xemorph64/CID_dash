import React from "react";
import { useApp } from "@/store/AppStore";
import { Network, Users, FileText, Lightbulb, Clock, Landmark, Phone, Crosshair, BarChart3, Route, ChevronLeft, ChevronRight } from "lucide-react";

const NAV = [
  { id: "overview", label: "Case Overview", icon: FileText },
  { id: "network", label: "Network", icon: Network },
  { id: "entities", label: "Entities", icon: Users },
  { id: "evidence", label: "Evidence", icon: FileText },
  { id: "leads", label: "Leads", icon: Lightbulb },
  { id: "timeline", label: "Timeline", icon: Clock },
  { id: "financial", label: "Financial Activity", icon: Landmark },
  { id: "communication", label: "Communication", icon: Phone },
  { id: "disruption", label: "Disruption Analysis", icon: Crosshair },
  { id: "paths", label: "Path Explorer", icon: Route },
  { id: "analytics", label: "Analytics", icon: BarChart3 },
];

export default function LeftNavigator({ collapsed, setCollapsed, view, setView }) {
  const { activeLayer, setActiveLayer } = useApp();
  return (
    <aside className={`relative shrink-0 border-r border-border bg-sidebar transition-all duration-200 ${collapsed ? "w-14" : "w-56"}`}>
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between px-3 py-3">
          {!collapsed && <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Investigation</span>}
          <button onClick={() => setCollapsed((c) => !c)} className="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground">
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>
        <nav className="flex-1 overflow-y-auto scrollbar-thin px-2 pb-4">
          {NAV.map((item) => {
            const Icon = item.icon;
            const active = view === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setView(item.id)}
                title={item.label}
                className={`mb-0.5 flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition ${active ? "bg-primary/15 font-medium text-primary" : "text-sidebar-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-foreground"} ${collapsed ? "justify-center" : ""}`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </button>
            );
          })}
        </nav>

        {!collapsed && (
          <div className="border-t border-border p-3">
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Graph layer</p>
            <select
              value={activeLayer}
              onChange={(e) => setActiveLayer(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="all">All relationships</option>
              <option value="communication">Communication</option>
              <option value="financial">Financial</option>
              <option value="locations">Locations</option>
              <option value="vehicles">Vehicles</option>
              <option value="organizations">Organizations</option>
            </select>
          </div>
        )}
      </div>
    </aside>
  );
}