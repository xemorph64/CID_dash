import React from "react";
import { useApp } from "@/store/AppStore";
import { INVESTIGATIONS, TIMELINE_EVENTS } from "@/data/mockData";
import { Play, Pause, SkipBack, SkipForward, Clock } from "lucide-react";

const DATES = [...new Set(TIMELINE_EVENTS.map((t) => t.date))].sort();

export default function TimelineControl() {
  const { timelineDate, setTimelineDate, timelinePlaying, setTimelinePlaying, currentInvestigationId } = useApp();
  const inv = INVESTIGATIONS.find((i) => i.id === currentInvestigationId);

  const jump = (dir) => {
    const idx = DATES.indexOf(timelineDate);
    const next = dir === "back" ? Math.max(0, idx - 1) : Math.min(DATES.length - 1, idx + 1);
    setTimelineDate(DATES[next]);
  };

  const eventsOnDate = TIMELINE_EVENTS.filter((t) => t.date <= timelineDate);

  return (
    <div className="border-t border-border bg-card px-4 py-3">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1">
          <button onClick={() => jump("back")} className="rounded p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground"><SkipBack className="h-4 w-4" /></button>
          <button onClick={() => setTimelinePlaying(!timelinePlaying)} className="rounded-md bg-primary p-1.5 text-primary-foreground hover:opacity-90">
            {timelinePlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </button>
          <button onClick={() => jump("fwd")} className="rounded p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground"><SkipForward className="h-4 w-4" /></button>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Clock className="h-3.5 w-3.5" />
          <span className="font-mono text-foreground">{timelineDate}</span>
        </div>

        <div className="relative flex-1">
          <input
            type="range"
            min={0}
            max={DATES.length - 1}
            value={Math.max(0, DATES.indexOf(timelineDate))}
            onChange={(e) => setTimelineDate(DATES[Number(e.target.value)])}
            className="h-1 w-full cursor-pointer appearance-none rounded-full bg-border accent-primary"
          />
          <div className="mt-1.5 flex justify-between text-[10px] text-muted-foreground">
            <span>{DATES[0]}</span>
            <span>{DATES[DATES.length - 1]}</span>
          </div>
        </div>

        <div className="hidden items-center gap-1.5 text-xs text-muted-foreground md:flex">
          <span className="rounded bg-accent px-2 py-1 font-medium text-foreground">{eventsOnDate.length}</span> events visible
        </div>
      </div>

      <div className="mt-2 flex flex-wrap gap-1.5">
        {TIMELINE_EVENTS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTimelineDate(t.date)}
            className={`rounded-full border px-2 py-0.5 text-[10px] transition ${t.date <= timelineDate ? "border-primary/40 bg-primary/10 text-primary" : "border-border text-muted-foreground opacity-50"}`}
            title={t.title}
          >
            {t.date}
          </button>
        ))}
      </div>
    </div>
  );
}