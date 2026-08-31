"use client";

import React, { useState } from "react";
import { Terminal, ChevronDown, ChevronUp, CheckCircle2, XCircle, Clock, Trash2, ShieldAlert } from "lucide-react";
import { ExecutionLog } from "@/types/workflow";

interface ExecutionLogsPanelProps {
  logs: ExecutionLog[];
  status: "idle" | "running" | "completed" | "failed";
  onClear: () => void;
}

export function ExecutionLogsPanel({ logs, status, onClear }: ExecutionLogsPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/90 shadow-2xl backdrop-blur-md overflow-hidden transition-all duration-300">
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-2.5 bg-slate-900/90 border-b border-slate-800 cursor-pointer select-none"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2.5">
          <Terminal className="h-4 w-4 text-sky-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Inngest Execution Telemetry & Step Logs ({logs.length})
          </span>
          {status === "running" && (
            <span className="h-2 w-2 rounded-full bg-amber-400 animate-ping"></span>
          )}
        </div>

        <div className="flex items-center gap-3">
          {logs.length > 0 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onClear();
              }}
              className="text-[11px] text-slate-400 hover:text-rose-400 flex items-center gap-1 transition-colors"
              title="Clear Logs"
            >
              <Trash2 className="h-3 w-3" /> Clear
            </button>
          )}
          {isExpanded ? <ChevronDown className="h-4 w-4 text-slate-400" /> : <ChevronUp className="h-4 w-4 text-slate-400" />}
        </div>
      </div>

      {/* Log Entries Body */}
      {isExpanded && (
        <div className="max-h-[220px] overflow-y-auto p-3 space-y-2 text-xs font-mono">
          {logs.length === 0 ? (
            <div className="text-center py-6 text-slate-500 flex flex-col items-center gap-1.5 font-sans">
              <Clock className="h-5 w-5 text-slate-600" />
              <span>Ready for execution. Click &apos;Run Workflow&apos; to trigger Inngest step evaluations.</span>
            </div>
          ) : (
            logs.map((log, index) => (
              <div
                key={log.stepId + index}
                className="rounded-lg border border-slate-800/80 bg-slate-900/60 p-2.5 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="rounded bg-sky-950 px-1.5 py-0.5 text-[10px] font-bold text-sky-400 border border-sky-800/50">
                      STEP {index + 1}
                    </span>
                    <span className="font-semibold text-slate-200">{log.nodeLabel}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-500 flex items-center gap-1">
                      <Clock className="h-3 w-3" /> {log.durationMs}ms
                    </span>
                    {log.decision === "YES" && (
                      <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3" /> YES
                      </span>
                    )}
                    {log.decision === "NO" && (
                      <span className="rounded bg-rose-500/20 px-2 py-0.5 text-[10px] font-bold text-rose-400 border border-rose-500/30 flex items-center gap-1">
                        <XCircle className="h-3 w-3" /> NO
                      </span>
                    )}
                  </div>
                </div>

                {log.prompt && (
                  <div className="mt-1.5 text-[11px] text-slate-400">
                    <span className="text-slate-500">Prompt:</span> &ldquo;{log.prompt}&rdquo;
                  </div>
                )}
                {log.details && (
                  <div className="mt-1 text-[10px] text-slate-500 flex items-center gap-1">
                    <ShieldAlert className="h-3 w-3 text-amber-500" /> {log.details}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
