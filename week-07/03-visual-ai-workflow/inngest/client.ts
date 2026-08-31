import { Inngest } from "inngest";

export const inngest = new Inngest({
  id: "visual-ai-workflow",
  isDev: process.env.NODE_ENV !== "production" || process.env.INNGEST_DEV === "true",
});
