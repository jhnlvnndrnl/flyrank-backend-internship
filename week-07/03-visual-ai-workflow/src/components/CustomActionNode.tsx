"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Zap, CheckCircle } from "lucide-react";
import { ActionNodeData } from "@/types/workflow";

export const CustomActionNode = memo(({ data, selected }: NodeProps) => {
  const nodeData = data as unknown as ActionNodeData;
  const status = nodeData.status || "idle";

  return (
    <div
      className={`relative min-w-[240px] max-w-[280px] rounded-xl border-2 bg-gradient-to-br from-slate-900 to-slate-950 p-3.5 shadow-lg backdrop-blur-md transition-all duration-300 ${
        selected ? "border-purple-400 ring-2 ring-purple-400/30" : "border-purple-600/50 hover:border-purple-500"
      } ${status === "completed" ? "border-emerald-500 ring-2 ring-emerald-500/20" : ""}`}
    >
      {/* Input Handle at Top */}
      <Handle
        type="target"
        position={Position.Top}
        className="!h-3.5 !w-3.5 !rounded-full !border-2 !border-slate-900 !bg-purple-400"
      />

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-purple-500/20 text-purple-400 border border-purple-500/30">
            <Zap className="h-4 w-4" />
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400">Terminal Action</span>
            <h4 className="text-xs font-bold text-slate-100">{nodeData.label || "Action Step"}</h4>
          </div>
        </div>

        {status === "completed" && (
          <span className="flex items-center gap-1 rounded-full bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/40">
            <CheckCircle className="h-3 w-3" /> Done
          </span>
        )}
      </div>
    </div>
  );
});

CustomActionNode.displayName = "CustomActionNode";
