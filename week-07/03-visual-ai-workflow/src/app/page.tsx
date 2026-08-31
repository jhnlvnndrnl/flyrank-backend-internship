"use client";

import React from "react";
import { WorkflowEditor } from "@/components/WorkflowEditor";
import { GitBranch, Radio } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col bg-slate-950">
      {/* Top Navbar */}
      <header className="flex h-[60px] items-center justify-between border-b border-slate-800/80 bg-slate-950/90 px-6 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 shadow-lg shadow-sky-500/20">
            <GitBranch className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-extrabold tracking-tight text-white flex items-center gap-2">
              Visual AI Workflow System
              <span className="rounded-full bg-sky-500/20 px-2 py-0.5 text-[10px] font-semibold text-sky-400 border border-sky-500/30">
                Week 7
              </span>
            </h1>
            <p className="text-[11px] text-slate-400">
              React Flow Visual Canvas · Inngest Boolean Traversal · OpenAI Decision Nodes
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/90 px-3 py-1 text-xs text-slate-300">
            <Radio className="h-3.5 w-3.5 text-emerald-400 animate-pulse" />
            <span className="text-[11px] font-medium">Inngest Engine Active</span>
          </div>
        </div>
      </header>

      {/* Visual Canvas Area */}
      <div className="flex-1">
        <WorkflowEditor />
      </div>
    </main>
  );
}
