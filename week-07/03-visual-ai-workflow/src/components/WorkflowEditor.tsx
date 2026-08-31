"use client";

import React, { useState, useCallback, useMemo } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  BackgroundVariant,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { CustomDecisionNode } from "./CustomDecisionNode";
import { CustomStartNode } from "./CustomStartNode";
import { CustomActionNode } from "./CustomActionNode";
import { WorkflowControls } from "./WorkflowControls";
import { ExecutionLogsPanel } from "./ExecutionLogsPanel";
import { NodeConfigSidebar } from "./NodeConfigSidebar";
import { DEFAULT_WORKFLOWS } from "@/lib/defaultWorkflows";
import { ExecutionLog, DecisionNodeData } from "@/types/workflow";
import { downloadJson } from "@/lib/utils";

export function WorkflowEditor() {
  const initialTemplate = DEFAULT_WORKFLOWS[0];

  const [nodes, setNodes, onNodesChange] = useNodesState(initialTemplate.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialTemplate.edges);
  const [inputContext, setInputContext] = useState(initialTemplate.inputExample);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [executionLogs, setExecutionLogs] = useState<ExecutionLog[]>([]);
  const [executionStatus, setExecutionStatus] = useState<"idle" | "running" | "completed" | "failed">("idle");

  const nodeTypes = useMemo(
    () => ({
      decisionNode: CustomDecisionNode,
      startNode: CustomStartNode,
      actionNode: CustomActionNode,
    }),
    []
  );

  const onConnect = useCallback(
    (params: Connection) => {
      const isYesHandle = params.sourceHandle === "yes";
      const isNoHandle = params.sourceHandle === "no";

      const newEdge: Edge = {
        ...params,
        id: `e-${params.source}-${params.target}-${Date.now()}`,
        animated: true,
        label: isYesHandle ? "YES" : isNoHandle ? "NO" : undefined,
        data: { condition: isYesHandle ? "YES" : isNoHandle ? "NO" : undefined },
        style: {
          stroke: isYesHandle ? "#10b981" : isNoHandle ? "#ef4444" : "#64748b",
          strokeWidth: 2,
        },
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges]
  );

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const handleUpdateNode = useCallback(
    (nodeId: string, updatedData: Partial<DecisionNodeData>) => {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === nodeId) {
            return {
              ...node,
              data: {
                ...node.data,
                ...updatedData,
              },
            };
          }
          return node;
        })
      );
    },
    [setNodes]
  );

  const handleDeleteNode = useCallback(
    (nodeId: string) => {
      setNodes((nds) => nds.filter((n) => n.id !== nodeId));
      setEdges((eds) => eds.filter((e) => e.source !== nodeId && e.target !== nodeId));
      setSelectedNode(null);
    },
    [setNodes, setEdges]
  );

  const handleAddDecisionNode = useCallback(() => {
    const id = `decision-${Date.now()}`;
    const newNode: Node = {
      id,
      type: "decisionNode",
      position: { x: 350 + Math.random() * 80, y: 200 + Math.random() * 80 },
      data: {
        label: "New AI Decision",
        prompt: "Is this request valid?",
        status: "idle",
      },
    };
    setNodes((nds) => [...nds, newNode]);
  }, [setNodes]);

  const handleAddActionNode = useCallback(() => {
    const id = `action-${Date.now()}`;
    const newNode: Node = {
      id,
      type: "actionNode",
      position: { x: 550 + Math.random() * 80, y: 250 + Math.random() * 80 },
      data: {
        label: "Execute Outcome",
        status: "idle",
      },
    };
    setNodes((nds) => [...nds, newNode]);
  }, [setNodes]);

  const handleSelectTemplate = useCallback(
    (templateId: string) => {
      const template = DEFAULT_WORKFLOWS.find((t) => t.id === templateId) || DEFAULT_WORKFLOWS[0];
      setNodes(template.nodes);
      setEdges(template.edges);
      setInputContext(template.inputExample);
      setExecutionLogs([]);
      setExecutionStatus("idle");
      setSelectedNode(null);
    },
    [setNodes, setEdges]
  );

  const handleReset = useCallback(() => {
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        data: {
          ...n.data,
          status: "idle",
          decision: undefined,
        },
      }))
    );
    setEdges((eds) =>
      eds.map((e) => ({
        ...e,
        style: {
          ...e.style,
          strokeWidth: 2,
          filter: "none",
        },
      }))
    );
    setExecutionLogs([]);
    setExecutionStatus("idle");
  }, [setNodes, setEdges]);

  // Execute Workflow via Inngest + Step Evaluation
  const handleRunWorkflow = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setExecutionStatus("running");
    setExecutionLogs([]);

    // Reset node visually first
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        data: {
          ...n.data,
          status: "idle",
          decision: undefined,
        },
      }))
    );

    // Notify backend Inngest runner
    try {
      fetch("/api/workflow/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nodes, edges, inputContext }),
      }).catch((e) => console.warn("Inngest dispatch notice:", e));
    } catch {
      // Background dispatch
    }

    // Step-by-step traversal with live animation
    const currentNodes = [...nodes];
    const currentEdges = [...edges];

    let activeNode = currentNodes.find((n) => n.type === "startNode") || currentNodes[0];
    let stepCount = 0;
    const maxSteps = 15;

    while (activeNode && stepCount < maxSteps) {
      stepCount++;
      const nodeId = activeNode.id;

      // Highlight current active node
      setNodes((nds) =>
        nds.map((n) => (n.id === nodeId ? { ...n, data: { ...n.data, status: "running" } } : n))
      );

      await new Promise((r) => setTimeout(r, 600));

      const startTime = Date.now();

      if (activeNode.type === "decisionNode" || activeNode.data?.prompt) {
        const prompt = (activeNode.data?.prompt as string) || (activeNode.data?.label as string);

        let decision: "YES" | "NO" = "YES";
        let evalSource = "Engine";

        try {
          const res = await fetch("/api/evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt, inputContext }),
          });
          const data = await res.json();
          decision = data.decision || "YES";
          evalSource = data.evaluatedWith || "LLM";
        } catch {
          decision = "YES";
        }

        const durationMs = Date.now() - startTime;

        // Update node to evaluated state
        setNodes((nds) =>
          nds.map((n) =>
            n.id === nodeId ? { ...n, data: { ...n.data, status: "evaluated", decision } } : n
          )
        );

        setExecutionLogs((prev) => [
          ...prev,
          {
            stepId: `step-${stepCount}`,
            nodeId,
            nodeLabel: (activeNode.data?.label as string) || "Decision Step",
            prompt,
            decision,
            durationMs,
            timestamp: new Date().toLocaleTimeString(),
            details: `Evaluated by ${evalSource}`,
          },
        ]);

        // Find matching active outgoing edge
        const outgoingEdges = currentEdges.filter((e) => e.source === nodeId);
        const activeEdge = outgoingEdges.find(
          (e) =>
            e.sourceHandle === decision.toLowerCase() ||
            e.data?.condition === decision ||
            e.label?.toUpperCase() === decision
        ) || outgoingEdges[0];

        if (activeEdge) {
          // Highlight edge
          setEdges((eds) =>
            eds.map((e) =>
              e.id === activeEdge.id
                ? {
                    ...e,
                    style: {
                      ...e.style,
                      stroke: decision === "YES" ? "#10b981" : "#ef4444",
                      strokeWidth: 4,
                      filter: "drop-shadow(0 0 6px rgba(16, 185, 129, 0.6))",
                    },
                  }
                : e
            )
          );

          await new Promise((r) => setTimeout(r, 600));
          activeNode = currentNodes.find((n) => n.id === activeEdge.target) || null!;
        } else {
          break;
        }
      } else {
        // Start or terminal action node
        const durationMs = Date.now() - startTime;
        setNodes((nds) =>
          nds.map((n) => (n.id === nodeId ? { ...n, data: { ...n.data, status: "completed" } } : n))
        );

        setExecutionLogs((prev) => [
          ...prev,
          {
            stepId: `step-${stepCount}`,
            nodeId,
            nodeLabel: (activeNode.data?.label as string) || "Action Node",
            durationMs,
            timestamp: new Date().toLocaleTimeString(),
            details: "Node reached and processed",
          },
        ]);

        const nextEdge = currentEdges.find((e) => e.source === nodeId);
        if (nextEdge) {
          activeNode = currentNodes.find((n) => n.id === nextEdge.target) || null!;
        } else {
          break;
        }
      }
    }

    setIsRunning(false);
    setExecutionStatus("completed");
  };

  const handleExportJson = () => {
    downloadJson({ nodes, edges, inputContext }, `workflow-${Date.now()}.json`);
  };

  const handleImportJson = (jsonString: string) => {
    try {
      const parsed = JSON.parse(jsonString);
      if (parsed.nodes && parsed.edges) {
        setNodes(parsed.nodes);
        setEdges(parsed.edges);
        if (parsed.inputContext) setInputContext(parsed.inputContext);
        setExecutionLogs([]);
        setExecutionStatus("idle");
      }
    } catch (err) {
      alert("Invalid workflow JSON format.");
    }
  };

  return (
    <div className="relative flex h-[calc(100vh-60px)] w-full flex-col bg-slate-950">
      {/* Top Floating Controls */}
      <div className="absolute left-4 top-4 z-10 w-[calc(100%-2rem)] max-w-5xl">
        <WorkflowControls
          onRun={handleRunWorkflow}
          isRunning={isRunning}
          onReset={handleReset}
          onAddDecisionNode={handleAddDecisionNode}
          onAddActionNode={handleAddActionNode}
          onSelectTemplate={handleSelectTemplate}
          onExportJson={handleExportJson}
          onImportJson={handleImportJson}
          inputContext={inputContext}
          setInputContext={setInputContext}
        />
      </div>

      {/* Main React Flow Canvas */}
      <div className="h-full w-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.3 }}
          className="bg-slate-950"
        >
          <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#334155" />
          <Controls className="!bg-slate-900 !border-slate-800 !text-slate-300 [&>button]:!border-slate-800 [&>button]:!bg-slate-900 [&>button]:!fill-slate-300 hover:[&>button]:!bg-slate-800" />
          <MiniMap
            nodeStrokeColor="#38bdf8"
            nodeColor="#1e293b"
            maskColor="rgba(15, 23, 42, 0.7)"
            className="!bg-slate-900/90 !border !border-slate-800 !rounded-lg"
          />
        </ReactFlow>
      </div>

      {/* Bottom Floating Execution Logs Panel */}
      <div className="absolute bottom-4 left-4 z-10 w-[calc(100%-2rem)] max-w-2xl">
        <ExecutionLogsPanel
          logs={executionLogs}
          status={executionStatus}
          onClear={() => setExecutionLogs([])}
        />
      </div>

      {/* Right Configuration Sidebar */}
      <NodeConfigSidebar
        node={selectedNode}
        onClose={() => setSelectedNode(null)}
        onUpdateNode={handleUpdateNode}
        onDeleteNode={handleDeleteNode}
      />
    </div>
  );
}
