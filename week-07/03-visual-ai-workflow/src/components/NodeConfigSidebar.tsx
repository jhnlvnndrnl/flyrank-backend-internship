"use client";

import React from "react";
import { Node } from "@xyflow/react";
import { X, Sparkles, Sliders, Trash2 } from "lucide-react";
import { DecisionNodeData } from "@/types/workflow";

interface NodeConfigSidebarProps {
  node: Node | null;
  onClose: () => void;
  onUpdateNode: (nodeId: string, updatedData: Partial<DecisionNodeData>) => void;
  onDeleteNode: (nodeId: string) => void;
}

export function NodeConfigSidebar({
  node,
  onClose,
  onUpdateNode,
  onDeleteNode,
}: NodeConfigSidebarProps) {
  if (!node) return null;

  const nodeData = node.data as unknown as DecisionNodeData;
  const isDecision = node.type === "decisionNode";

  return (
    <div className="absolute right-4 top-20 z-20 w-80 rounded-xl border border-slate-800 bg-slate-950/95 p-4 shadow-2xl backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Sliders className="h-4 w-4 text-sky-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Configure Node
          </h3>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-3.5 space-y-3.5 text-xs">
        {/* Node Label */}
        <div>
          <label className="block text-[11px] font-semibold text-slate-400 mb-1">
            Node Title
          </label>
          <input
            type="text"
            value={nodeData.label || ""}
            onChange={(e) => onUpdateNode(node.id, { label: e.target.value })}
            className="w-full rounded-lg border border-slate-800 bg-slate-900 px-2.5 py-1.5 text-xs text-slate-200 focus:border-sky-500 outline-none"
          />
        </div>

        {/* Decision Prompt */}
        {isDecision && (
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1">
              <Sparkles className="h-3 w-3 text-sky-400" /> AI Decision Prompt / Boolean Question
            </label>
            <textarea
              rows={4}
              value={nodeData.prompt || ""}
              onChange={(e) => onUpdateNode(node.id, { prompt: e.target.value })}
              placeholder="e.g. Is this message asking for urgent support?"
              className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-xs text-slate-200 focus:border-sky-500 outline-none font-mono resize-none leading-relaxed"
            />
            <p className="mt-1 text-[10px] text-slate-500">
              The LLM will evaluate this question against the input context and return strictly YES or NO.
            </p>
          </div>
        )}

        {/* Delete Node */}
        <div className="pt-2 border-t border-slate-800">
          <button
            onClick={() => onDeleteNode(node.id)}
            className="w-full flex items-center justify-center gap-1.5 rounded-lg border border-rose-500/40 bg-rose-500/10 py-1.5 text-xs font-semibold text-rose-400 hover:bg-rose-500/20 transition-all"
          >
            <Trash2 className="h-3.5 w-3.5" /> Delete Node
          </button>
        </div>
      </div>
    </div>
  );
}
