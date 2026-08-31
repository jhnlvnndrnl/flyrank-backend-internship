"use client";

import React, { useRef } from "react";
import { Play, RotateCcw, Plus, Download, Upload, Layers, Loader2, Sparkles } from "lucide-react";
import { DEFAULT_WORKFLOWS } from "@/lib/defaultWorkflows";

interface WorkflowControlsProps {
  onRun: () => void;
  isRunning: boolean;
  onReset: () => void;
  onAddDecisionNode: () => void;
  onAddActionNode: () => void;
  onSelectTemplate: (templateId: string) => void;
  onExportJson: () => void;
  onImportJson: (jsonString: string) => void;
  inputContext: string;
  setInputContext: (val: string) => void;
}

export function WorkflowControls({
  onRun,
  isRunning,
  onReset,
  onAddDecisionNode,
  onAddActionNode,
  onSelectTemplate,
  onExportJson,
  onImportJson,
  inputContext,
  setInputContext,
}: WorkflowControlsProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      if (content) onImportJson(content);
    };
    reader.readAsText(file);
    e.target.value = "";
  };

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-950/80 p-3.5 shadow-2xl backdrop-blur-md">
      {/* Top action row */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Left: Templates & Node additions */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Template Selector */}
          <div className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-900/90 px-2.5 py-1 text-xs text-slate-300">
            <Layers className="h-3.5 w-3.5 text-sky-400" />
            <select
              onChange={(e) => onSelectTemplate(e.target.value)}
              defaultValue="support-triage"
              className="bg-transparent text-xs font-medium text-slate-200 outline-none cursor-pointer"
            >
              {DEFAULT_WORKFLOWS.map((t) => (
                <option key={t.id} value={t.id} className="bg-slate-900 text-slate-200">
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={onAddDecisionNode}
            className="flex items-center gap-1.5 rounded-lg border border-sky-500/40 bg-sky-500/10 px-2.5 py-1 text-xs font-semibold text-sky-300 hover:bg-sky-500/20 transition-all"
          >
            <Plus className="h-3.5 w-3.5" /> Decision Node
          </button>

          <button
            onClick={onAddActionNode}
            className="flex items-center gap-1.5 rounded-lg border border-purple-500/40 bg-purple-500/10 px-2.5 py-1 text-xs font-semibold text-purple-300 hover:bg-purple-500/20 transition-all"
          >
            <Plus className="h-3.5 w-3.5" /> Action Node
          </button>
        </div>

        {/* Right: Run and Persistence buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={onExportJson}
            className="flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-900/80 px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-800 transition-all"
            title="Export Graph to JSON"
          >
            <Download className="h-3.5 w-3.5" /> Export
          </button>

          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-900/80 px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-800 transition-all"
            title="Import Graph from JSON"
          >
            <Upload className="h-3.5 w-3.5" /> Import
          </button>
          <input ref={fileInputRef} type="file" accept=".json" onChange={handleFileUpload} className="hidden" />

          <button
            onClick={onReset}
            disabled={isRunning}
            className="flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-900/80 px-2.5 py-1 text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-800 disabled:opacity-50 transition-all"
            title="Reset Graph to Initial State"
          >
            <RotateCcw className="h-3.5 w-3.5" /> Reset
          </button>

          <button
            onClick={onRun}
            disabled={isRunning}
            className={`flex items-center gap-2 rounded-lg px-4 py-1.5 text-xs font-bold text-white shadow-lg transition-all ${
              isRunning
                ? "bg-amber-600 cursor-not-allowed opacity-80"
                : "bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 shadow-emerald-500/20 active:scale-95"
            }`}
          >
            {isRunning ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" /> Inngest Running...
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" /> Run Workflow
              </>
            )}
          </button>
        </div>
      </div>

      {/* Input context payload box */}
      <div className="flex flex-col gap-1">
        <label className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
          <Sparkles className="h-3 w-3 text-sky-400" /> Inbound Context / Simulation Payload:
        </label>
        <textarea
          rows={2}
          value={inputContext}
          onChange={(e) => setInputContext(e.target.value)}
          placeholder="Enter message text to evaluate against graph decision nodes..."
          className="w-full rounded-lg border border-slate-800 bg-slate-900/90 p-2 text-xs text-slate-200 placeholder:text-slate-600 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 outline-none resize-none font-mono"
        />
      </div>
    </div>
  );
}
