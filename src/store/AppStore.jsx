import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import mockApi from "@/services/mockApi";
import { ENTITIES, RELATIONSHIPS, EVIDENCE, LEADS, NOTES, TIMELINE_EVENTS } from "@/data/mockData";

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [theme, setTheme] = useState("dark");
  const [investigations, setInvestigations] = useState([]);
  const [currentInvestigationId, setCurrentInvestigationId] = useState("inv-monsoon");
  const [recentlyViewed, setRecentlyViewed] = useState([]);
  const [pinned, setPinned] = useState([]);
  const [savedLeads, setSavedLeads] = useState([]);

  // workspace state
  const [selectedEntityId, setSelectedEntityId] = useState(null);
  const [selectedRelationshipId, setSelectedRelationshipId] = useState(null);
  const [focusEntityId, setFocusEntityId] = useState(null);
  const [activeLayer, setActiveLayer] = useState("all");
  const [timelineDate, setTimelineDate] = useState("2024-08-31");
  const [timelinePlaying, setTimelinePlaying] = useState(false);
  const [evidenceDrawerOpen, setEvidenceDrawerOpen] = useState(false);
  const [evidenceItems, setEvidenceItems] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [tabs, setTabs] = useState([{ id: "overview", label: "Network Overview", closable: false }]);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [notes, setNotes] = useState(NOTES);
  const [leads, setLeads] = useState(LEADS);
  const [disruptionSelection, setDisruptionSelection] = useState([]);
  const [pathSource, setPathSource] = useState(null);
  const [pathTarget, setPathTarget] = useState(null);
  const [highlightPath, setHighlightPath] = useState(null);
  const [toasts, setToasts] = useState([]);

  // theme application
  useEffect(() => {
    const root = document.documentElement;
    if (theme === "light") root.classList.add("light");
    else root.classList.remove("light");
  }, [theme]);

  // load investigations + meta
  useEffect(() => {
    (async () => {
      const [invs, rv, pin, sl] = await Promise.all([
        mockApi.getInvestigations(),
        mockApi.getRecentlyViewed(),
        mockApi.getPinned(),
        mockApi.getSavedLeads(),
      ]);
      setInvestigations(invs);
      setRecentlyViewed(rv);
      setPinned(pin);
      setSavedLeads(sl);
    })();
  }, []);

  // command palette hotkey
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCommandPaletteOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  // timeline playback
  useEffect(() => {
    if (!timelinePlaying) return;
    const dates = TIMELINE_EVENTS.map((t) => t.date).sort();
    let idx = 0;
    const tick = () => {
      idx = (idx + 1) % dates.length;
      setTimelineDate(dates[idx]);
    };
    const id = setInterval(tick, 1400);
    return () => clearInterval(id);
  }, [timelinePlaying]);

  const pushToast = useCallback((message, opts = {}) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, message, ...opts }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3200);
  }, []);

  const pushRecentlyViewed = useCallback((id) => {
    setRecentlyViewed((rv) => [id, ...rv.filter((x) => x !== id)].slice(0, 12));
  }, []);

  const selectEntity = useCallback((id) => {
    setSelectedEntityId(id);
    setSelectedRelationshipId(null);
    if (id) pushRecentlyViewed(id);
  }, [pushRecentlyViewed]);

  const selectRelationship = useCallback((id) => {
    setSelectedRelationshipId(id);
    setSelectedEntityId(null);
  }, []);

  const openEvidence = useCallback(async (evidenceIds) => {
    const ids = Array.isArray(evidenceIds) ? evidenceIds : [evidenceIds];
    const items = EVIDENCE.filter((e) => ids.includes(e.id));
    setEvidenceItems(items);
    setEvidenceDrawerOpen(true);
  }, []);

  const openEvidenceForRelationship = useCallback(async (relationshipId) => {
    const rel = RELATIONSHIPS.find((r) => r.id === relationshipId);
    if (!rel) return;
    const items = EVIDENCE.filter((e) => (rel.evidence || []).includes(e.id));
    setEvidenceItems(items);
    setEvidenceDrawerOpen(true);
  }, []);

  const addNote = useCallback((scope, text) => {
    const note = {
      id: `N${Date.now()}`,
      scope,
      author: "Demo Investigator",
      ts: new Date().toISOString(),
      text,
      pinned: false,
    };
    setNotes((n) => [note, ...n]);
    pushToast("Note saved");
    return note;
  }, [pushToast]);

  const deleteNote = useCallback((id) => {
    setNotes((n) => n.filter((x) => x.id !== id));
  }, []);

  const togglePinNote = useCallback((id) => {
    setNotes((n) => n.map((x) => (x.id === id ? { ...x, pinned: !x.pinned } : x)));
  }, []);

  const updateLead = useCallback((leadId, status) => {
    setLeads((ls) => ls.map((l) => (l.id === leadId ? { ...l, status } : l)));
  }, []);

  const toggleSaveLead = useCallback((leadId) => {
    setSavedLeads((sl) => (sl.includes(leadId) ? sl.filter((x) => x !== leadId) : [...sl, leadId]));
  }, []);

  const openTab = useCallback((tab) => {
    setTabs((ts) => {
      if (ts.find((t) => t.id === tab.id)) return ts;
      return [...ts, tab];
    });
    setActiveTab(tab.id);
  }, []);

  const closeTab = useCallback((tabId) => {
    setTabs((ts) => {
      const filtered = ts.filter((t) => t.id !== tabId);
      if (activeTab === tabId && filtered.length) setActiveTab(filtered[filtered.length - 1].id);
      return filtered;
    });
  }, [activeTab]);

  const value = {
    theme, setTheme: (t) => setTheme(t),
    investigations, currentInvestigationId, setCurrentInvestigationId,
    recentlyViewed, pinned, savedLeads,
    selectedEntityId, selectEntity,
    selectedRelationshipId, selectRelationship,
    focusEntityId, setFocusEntityId,
    activeLayer, setActiveLayer,
    timelineDate, setTimelineDate, timelinePlaying, setTimelinePlaying,
    evidenceDrawerOpen, setEvidenceDrawerOpen, evidenceItems, openEvidence, openEvidenceForRelationship,
    activeTab, setActiveTab, tabs, openTab, closeTab,
    commandPaletteOpen, setCommandPaletteOpen,
    notes, addNote, deleteNote, togglePinNote,
    leads, updateLead, toggleSaveLead,
    disruptionSelection, setDisruptionSelection,
    pathSource, setPathSource, pathTarget, setPathTarget, highlightPath, setHighlightPath,
    toasts, pushToast,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}