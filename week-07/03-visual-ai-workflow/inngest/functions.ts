import { inngest } from "./client";
import OpenAI from "openai";

interface WorkflowPayload {
  runId: string;
  inputContext: string;
  nodes: Array<{
    id: string;
    type: string;
    data: {
      label: string;
      prompt?: string;
      description?: string;
    };
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    sourceHandle?: string | null;
    label?: string;
    data?: {
      condition?: "YES" | "NO";
    };
  }>;
}

// Evaluate single decision prompt via OpenAI LLM or deterministic fallback
async function evaluateDecisionWithLLM(prompt: string, context: string): Promise<"YES" | "NO"> {
  const apiKey = process.env.OPENAI_API_KEY;

  if (apiKey && apiKey.trim() && !apiKey.includes("your_openai")) {
    try {
      const openai = new OpenAI({ apiKey });
      const response = await openai.chat.completions.create({
        model: process.env.OPENAI_MODEL || "gpt-4o-mini",
        temperature: 0.1,
        max_tokens: 10,
        messages: [
          {
            role: "system",
            content:
              "You are an AI decision engine in a workflow graph. You must answer ONLY with a single word: 'YES' or 'NO'. No punctuation, no markdown, no explanation.",
          },
          {
            role: "user",
            content: `CONTEXT / INPUT:\n"${context}"\n\nDECISION PROMPT / QUESTION:\n"${prompt}"\n\nRespond only with YES or NO:`,
          },
        ],
      });

      const text = response.choices[0]?.message?.content?.trim().toUpperCase() || "";
      if (text.includes("YES")) return "YES";
      if (text.includes("NO")) return "NO";
    } catch (err) {
      console.warn("LLM API error, falling back to heuristic engine:", err);
    }
  }

  // Built-in intelligent heuristic classification fallback
  const combined = (context + " " + prompt).toLowerCase();
  const negativeSignals = ["not", "no", "cancel", "refund", "broken", "angry", "bug", "urgent", "sales", "fail", "lead"];
  const positiveSignals = ["help", "support", "question", "info", "yes", "true", "billing", "account", "login", "feature"];

  let score = 0;
  positiveSignals.forEach((w) => {
    if (combined.includes(w)) score += 1;
  });
  negativeSignals.forEach((w) => {
    if (combined.includes(w)) score -= 1;
  });

  return score >= 0 ? "YES" : "NO";
}

export const executeVisualWorkflow = inngest.createFunction(
  {
    id: "execute-visual-workflow",
    name: "Execute Visual AI Workflow",
    retries: 2,
  },
  { event: "workflow/execute.requested" },
  async ({ event, step }) => {
    const payload = event.data as WorkflowPayload;
    const { runId, inputContext, nodes, edges } = payload;

    const visitedNodes: string[] = [];
    const executionLogs: Array<{
      stepId: string;
      nodeId: string;
      nodeLabel: string;
      prompt?: string;
      decision?: "YES" | "NO";
      timestamp: string;
      durationMs: number;
    }> = [];

    // Find start node or first node
    let currentNode = nodes.find((n) => n.type === "startNode") || nodes[0];
    if (!currentNode) {
      return { status: "failed", error: "No start node found in workflow." };
    }

    let iterations = 0;
    const maxIterations = 20;

    while (currentNode && iterations < maxIterations) {
      iterations++;
      const activeNode = currentNode;
      visitedNodes.push(activeNode.id);

      const startTime = Date.now();

      if (activeNode.type === "decisionNode" || activeNode.data?.prompt) {
        const prompt = activeNode.data.prompt || activeNode.data.label;

        // Inngest Step: Evaluate AI Decision Node
        const decision = await step.run(`evaluate-node-${activeNode.id}`, async () => {
          return await evaluateDecisionWithLLM(prompt, inputContext);
        });

        const durationMs = Date.now() - startTime;
        executionLogs.push({
          stepId: `step-${iterations}`,
          nodeId: activeNode.id,
          nodeLabel: activeNode.data.label,
          prompt,
          decision,
          timestamp: new Date().toISOString(),
          durationMs,
        });

        // Traverse along active edge matching YES/NO handle or condition
        const outgoingEdges = edges.filter((e) => e.source === activeNode.id);
        const matchingEdge = outgoingEdges.find(
          (e) =>
            e.sourceHandle === decision.toLowerCase() ||
            e.data?.condition === decision ||
            e.label?.toUpperCase() === decision
        ) || outgoingEdges[0];

        if (matchingEdge) {
          currentNode = nodes.find((n) => n.id === matchingEdge.target) || null!;
        } else {
          break;
        }
      } else {
        // Start or Action node step
        await step.run(`process-node-${activeNode.id}`, async () => {
          return { processed: true, label: activeNode.data.label };
        });

        executionLogs.push({
          stepId: `step-${iterations}`,
          nodeId: activeNode.id,
          nodeLabel: activeNode.data.label,
          timestamp: new Date().toISOString(),
          durationMs: Date.now() - startTime,
        });

        const nextEdge = edges.find((e) => e.source === activeNode.id);
        if (nextEdge) {
          currentNode = nodes.find((n) => n.id === nextEdge.target) || null!;
        } else {
          break;
        }
      }
    }

    return {
      runId,
      status: "completed",
      visitedNodes,
      executionLogs,
      completedAt: new Date().toISOString(),
    };
  }
);
