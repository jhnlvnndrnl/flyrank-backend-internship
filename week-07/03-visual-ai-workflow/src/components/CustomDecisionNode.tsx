"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Bot, CheckCircle2, XCircle, Loader2, Sparkles } from "lucide-react";
import { DecisionNodeData } from "@/types/workflow";

export const CustomDecisionNode = memo(({ id, data, selected }: NodeProps) => {
  const nodeData = data as unknown as DecisionNodeData;
  const status = nodeData.status || "idle";
  const decision = nodeData.decision;

  return (
    <div
      className={`relative min-w-[280px] max-w-[320px] rounded-xl border-2 bg-slate-900/95 p-4 shadow-xl backdrop-blur-md transition-all duration-300 ${
        selected ? "border-sky-400 ring-2 ring-sky-400/30" : "border-slate-700 hover:border-slate-500"
      } ${status === "running" ? "border-amber-400 ring-4 ring-amber-400/20 shadow-amber-500/20" : ""} ${
        status === "evaluated"
          ? decision === "YES"
            ? "border-emerald-500 ring-2 ring-emerald-500/20"
            : "border-rose-500 ring-2 ring-rose-500/20"
          : ""
      }`}
    >
      {/* Target input handle at Top */}
      <Handle
        type="target"
        position={Position.Top}
        className="!h-3.5 !w-3.5 !rounded-full !border-2 !border-slate-900 !bg-sky-400"
      />

      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-sky-500/20 text-sky-400 border border-sky-500/30">
            <Bot className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              {nodeData.label || "AI Decision Step"}
            </h4>
            <span className="text-[10px] text-slate-400">LLM Boolean Gate</span>
          </div>
        </div>

        {/* Status indicator badge */}
        <div>
          {status === "running" && (
            <span className="flex items-center gap-1 rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-medium text-amber-300 border border-amber-500/30 animate-pulse">
              <Loader2 className="h-3 w-3 animate-spin" /> Evaluating
            </span>
          )}
          {status === "evaluated" && decision === "YES" && (
            <span className="flex items-center gap-1 rounded-full bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/40">
              <CheckCircle2 className="h-3 w-3" /> YES
            </span>
          )}
          {status === "evaluated" && decision === "NO" && (
            <span className="flex items-center gap-1 rounded-full bg-rose-500/20 px-2 py-0.5 text-[10px] font-bold text-rose-400 border border-rose-500/40">
              <XCircle className="h-3 w-3" /> NO
            </span>
          )}
          {status === "idle" && (
            <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] font-medium text-slate-400 border border-slate-700">
              Ready
            </span>
          )}
        </div>
      </div>

      {/* Prompt / Decision Query Body */}
      <div className="mt-3">
        <div className="flex items-center gap-1 text-[11px] font-medium text-slate-400 mb-1">
          <Sparkles className="h-3 w-3 text-sky-400" /> Decision Prompt:
        </div>
        <p className="rounded-lg bg-slate-950/80 p-2.5 text-xs text-slate-200 border border-slate-800 leading-relaxed font-mono">
          &ldquo;{nodeData.prompt || "Is the condition met?"}&rdquo;
        </p>
      </div>

      {/* Branching Output Handles */}
      <div className="mt-4 flex items-center justify-between pt-2 border-t border-slate-800/80 text-[11px] font-bold">
        {/* Left / Bottom YES Handle */}
        <div className="flex items-center gap-1.5 text-emerald-400">
          <span className="inline-block h-2 w-2 rounded-full bg-emerald-500"></span>
          <span>YES</span>
        </div>

        {/* Right / Bottom NO Handle */}
        <div className="flex items-center gap-1.5 text-rose-400">
          <span>NO</span>
          <span className="inline-block h-2 w-2 rounded-full bg-rose-500"></span>
        </div>
      </div>

      {/* Actual handles for react flow connections */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="yes"
        className="!left-[25%] !h-3.5 !w-3.5 !rounded-full !border-2 !border-slate-900 !bg-emerald-500"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="no"
        className="!left-[75%] !h-3.5 !w-3.5 !rounded-full !border-2 !border-slate-900 !bg-rose-500"
      />
    </div>
  );
});

CustomDecisionNode.displayName = "CustomDecisionNode";
