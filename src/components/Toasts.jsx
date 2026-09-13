import React from "react";
import { useApp } from "@/store/AppStore";
import { CheckCircle2, Info, AlertTriangle } from "lucide-react";

export default function Toasts() {
  const { toasts } = useApp();
  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-[60] flex flex-col gap-2">
      {toasts.map((t) => (
        <div key={t.id} className="pointer-events-auto flex items-center gap-2 rounded-lg border border-border bg-popover px-3.5 py-2.5 text-sm text-foreground shadow-lg">
          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          {t.message}
        </div>
      ))}
    </div>
  );
}