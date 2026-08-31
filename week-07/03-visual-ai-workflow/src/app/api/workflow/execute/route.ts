import { NextRequest, NextResponse } from "next/server";
import { inngest } from "../../../../../inngest/client";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { nodes, edges, inputContext } = body;

    if (!nodes || !Array.isArray(nodes) || nodes.length === 0) {
      return NextResponse.json({ error: "Nodes array is required." }, { status: 400 });
    }

    const runId = `run_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;

    // Send event to Inngest for durable background orchestration
    let inngestEventId: string | null = null;
    try {
      const sendResult = await inngest.send({
        name: "workflow/execute.requested",
        data: {
          runId,
          inputContext: inputContext || "",
          nodes,
          edges: edges || [],
        },
      });
      inngestEventId = sendResult?.ids?.[0] || "sent";
    } catch (inngestErr) {
      console.warn("Inngest send notice (Inngest Dev Server might be running on :8288):", inngestErr);
    }

    return NextResponse.json({
      runId,
      inngestEventId,
      status: "queued",
      message: "Workflow run dispatched to Inngest and ready for client tracking.",
    });
  } catch (error: unknown) {
    const errMessage = error instanceof Error ? error.message : "Internal error";
    return NextResponse.json({ error: errMessage }, { status: 500 });
  }
}
