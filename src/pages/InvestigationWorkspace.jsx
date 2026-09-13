import React, { useState } from "react";
import { useApp } from "@/store/AppStore";
import TopBar from "@/components/investigation/TopBar";
import LeftNavigator from "@/components/investigation/LeftNavigator";
import KnowledgeGraph from "@/components/knowledge-graph/KnowledgeGraph";
import RightInspector from "@/components/investigation/RightInspector";
import EvidenceDrawer from "@/components/investigation/EvidenceDrawer";
import TimelineControl from "@/components/investigation/TimelineControl";
import LeadsView from "@/components/leads/LeadsView";
import DisruptionSimulator from "@/components/disruption/DisruptionSimulator";
import PathExplorer from "@/components/paths/PathExplorer";
import AnalyticsView from "@/components/analytics/AnalyticsView";
import { CaseOverview, EntityList, EvidenceList, TimelineView, ActivityView } from "@/components/investigation/WorkspacePanels";

export default function InvestigationWorkspace() {
  const [collapsed, setCollapsed] = useState(false);
  const [view, setView] = useState("network");
  const { evidenceDrawerOpen, pushToast } = useApp();

  const onExport = () => {
    pushToast("Summary exported (demo)");
  };

  const showGraph = view === "network" || view === "overview";

  return (
    <div className="flex h-screen flex-col bg-background">
      <TopBar onExport={onExport} />
      <div className="flex flex-1 overflow-hidden">
        <LeftNavigator collapsed={collapsed} setCollapsed={setCollapsed} view={view} setView={setView} />

        <div className="flex flex-1 flex-col overflow-hidden">
          {showGraph ? (
            <div className="flex flex-1 overflow-hidden">
              <div className="relative flex-1 overflow-hidden p-3">
                <KnowledgeGraph />
                {evidenceDrawerOpen && <EvidenceDrawer />}
              </div>
              <div className="w-80 shrink-0 border-l border-border bg-card">
                <RightInspector />
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-hidden">
              {view === "leads" && <LeadsView />}
              {view === "disruption" && <DisruptionSimulator />}
              {view === "paths" && <PathExplorer />}
              {view === "analytics" && <AnalyticsView />}
              {view === "entities" && <EntityList />}
              {view === "evidence" && <EvidenceList />}
              {view === "timeline" && <TimelineView />}
              {view === "financial" && <ActivityView kind="financial" />}
              {view === "communication" && <ActivityView kind="communication" />}
            </div>
          )}

          {showGraph && <TimelineControl />}
        </div>
      </div>
    </div>
  );
}