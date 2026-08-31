import { Node, Edge } from "@xyflow/react";

export type DecisionType = "YES" | "NO";

export interface DecisionNodeData extends Record<string, unknown> {
  label: string;
  prompt: string;
  description?: string;
  status?: "idle" | "running" | "evaluated" | "error";
  decision?: DecisionType;
}

export interface StartNodeData extends Record<string, unknown> {
  label: string;
  inputKey?: string;
}

export interface ActionNodeData extends Record<string, unknown> {
  label: string;
  actionType?: string;
  status?: "idle" | "running" | "completed" | "error";
}

export type CustomNodeType = Node<DecisionNodeData | StartNodeData | ActionNodeData>;

export interface ExecutionLog {
  stepId: string;
  nodeId: string;
  nodeLabel: string;
  prompt?: string;
  decision?: DecisionType;
  durationMs: number;
  timestamp: string;
  details?: string;
}

export interface WorkflowRunState {
  runId: string;
  status: "idle" | "running" | "completed" | "failed";
  activeNodeId?: string | null;
  activeEdgeId?: string | null;
  visitedNodes: string[];
  logs: ExecutionLog[];
  startedAt?: string;
  completedAt?: string;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  inputExample: string;
  nodes: Node[];
  edges: Edge[];
}
