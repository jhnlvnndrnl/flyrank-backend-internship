"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { PlayCircle, ArrowRight } from "lucide-react";
import { StartNodeData } from "@/types/workflow";

export const CustomStartNode = memo(({ data, selected }: NodeProps) => {
  const nodeData = data as unknown as StartNodeData;

  return (
    <div
      className={`relative min-w-[220px] rounded-xl border-2 bg-gradient-to-br from-slate-900 to-slate-950 p-3.5 shadow-lg backdrop-blur-md transition-all duration-300 ${
        selected ? "border-emerald-400 ring-2 ring-emerald-400/30" : "border-emerald-600/50 hover:border-emerald-500"
      }`}
    >
      <div className="flex items-center gap-2.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
          <PlayCircle className="h-5 w-5" />
        </div>
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">Workflow Trigger</span>
          <h4 className="text-xs font-bold text-slate-100">{nodeData.label || "Start Input"}</h4>
        </div>
      </div>

      <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-400">
        <span>Payload: context</span>
        <ArrowRight className="h-3 w-3 text-slate-500" />
      </div>

      {/* Outgoing connection handle */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!h-3.5 !w-3.5 !rounded-full !border-2 !border-slate-900 !bg-emerald-400"
      />
    </div>
  );
});

CustomStartNode.displayName = "CustomStartNode";
