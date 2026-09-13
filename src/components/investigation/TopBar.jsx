import React from "react";
import { useApp } from "@/store/AppStore";
import { INVESTIGATIONS } from "@/data/mockData";
import { ShieldCheck, Search, Undo2, Redo2, Save, Download, Settings, Sun, Moon, Command } from "lucide-react";

export default function TopBar({ onExport }) {
  const { currentInvestigationId, setCommandPaletteOpen, theme, setTheme, pushToast } = useApp();
  const inv = INVESTIGATIONS.find((i) => i.id === currentInvestigationId);

  return (
    <header className="flex h-14 shrink-0 items-center gap-3 border-b border-border bg-card px-4">
      <div className="flex items-center gap-2.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
          <ShieldCheck className="h-5 w-5" />
        </div>
        <div className="leading-tight">
          <div className="text-sm font-semibold tracking-tight text-foreground">C.I.D.</div>
          <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Criminal Intelligence</div>
        </div>
      </div>

      <div className="mx-2 h-7 w-px bg-border" />

      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <h1 className="truncate text-sm font-medium text-foreground">{inv?.title}</h1>
          <span className="shrink-0 rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-[10px] font-medium text-amber-500">DEMO</span>
        </div>
        <p className="truncate text-[11px] text-muted-foreground">{inv?.caseRef}</p>
      </div>

      <button
        onClick={() => setCommandPaletteOpen(true)}
        className="ml-auto flex h-8 items-center gap-2 rounded-md border border-border bg-accent px-3 text-xs text-muted-foreground transition hover:border-primary/40 hover:text-foreground"
      >
        <Search className="h-3.5 w-3.5" />
        <span className="hidden sm:inline">Search…</span>
        <kbd className="hidden items-center gap-0.5 rounded border border-border bg-background px-1 text-[10px] sm:flex"><Command className="h-2.5 w-2.5" />K</kbd>
      </button>

      <div className="flex items-center gap-0.5">
        <IconBtn label="Undo" onClick={() => pushToast("Nothing to undo")}><Undo2 className="h-4 w-4" /></IconBtn>
        <IconBtn label="Redo" onClick={() => pushToast("Nothing to redo")}><Redo2 className="h-4 w-4" /></IconBtn>
        <IconBtn label="Save workspace" onClick={() => pushToast("Workspace saved (demo)")}><Save className="h-4 w-4" /></IconBtn>
        <IconBtn label="Export summary" onClick={onExport}><Download className="h-4 w-4" /></IconBtn>
        <IconBtn label="Switch theme" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </IconBtn>
        <IconBtn label="Settings" onClick={() => pushToast("Settings — demo")}><Settings className="h-4 w-4" /></IconBtn>
      </div>
    </header>
  );
}

function IconBtn({ children, label, onClick }) {
  return (
    <button onClick={onClick} title={label} aria-label={label} className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition hover:bg-accent hover:text-foreground">
      {children}
    </button>
  );
}