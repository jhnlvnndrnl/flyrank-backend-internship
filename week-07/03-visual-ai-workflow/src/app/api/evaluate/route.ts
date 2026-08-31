import { NextRequest, NextResponse } from "next/server";
import OpenAI from "openai";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { prompt, inputContext } = body;

    if (!prompt) {
      return NextResponse.json({ error: "Prompt is required." }, { status: 400 });
    }

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
              content: `INPUT CONTEXT:\n"${inputContext || ""}"\n\nDECISION QUESTION:\n"${prompt}"\n\nAnswer only YES or NO:`,
            },
          ],
        });

        const rawText = response.choices[0]?.message?.content?.trim().toUpperCase() || "";
        const decision = rawText.includes("YES") ? "YES" : "NO";

        return NextResponse.json({
          decision,
          rawResponse: rawText,
          model: response.model,
          evaluatedWith: "OpenAI",
        });
      } catch (err: unknown) {
        console.warn("OpenAI API call failed, falling back to heuristic engine:", err);
      }
    }

    // Heuristic Fallback Engine
    const combined = ((inputContext || "") + " " + prompt).toLowerCase();
    const negativeTerms = ["not", "no", "cancel", "refund", "broken", "angry", "bug", "urgent", "sales", "fail", "lead", "spam", "toxic", "hate"];
    const positiveTerms = ["help", "support", "question", "info", "yes", "true", "billing", "account", "login", "feature", "clean", "safe"];

    let score = 0;
    positiveTerms.forEach((t) => {
      if (combined.includes(t)) score += 1;
    });
    negativeTerms.forEach((t) => {
      if (combined.includes(t)) score -= 1;
    });

    const fallbackDecision = score >= 0 ? "YES" : "NO";

    return NextResponse.json({
      decision: fallbackDecision,
      evaluatedWith: "Heuristic Fallback Engine",
      note: "Configure OPENAI_API_KEY in .env for live GPT model decisions.",
    });
  } catch (error: unknown) {
    const errMessage = error instanceof Error ? error.message : "Internal error";
    return NextResponse.json({ error: errMessage }, { status: 500 });
  }
}
