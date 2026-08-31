"""Inngest Background Functions."""

import datetime
import logging
import os
from typing import Any
import inngest
from .inngest_client import inngest_client
from .storage import update_report, get_summary

logger = logging.getLogger("report-api")


@inngest_client.create_function(
    fn_id="say-hello",
    name="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context, step: inngest.Step) -> str:
    """Stage 1: Hello from background worker with 5-second sleep."""
    await step.sleep("wait-5-seconds", datetime.timedelta(seconds=5))
    return "Hello from the background!"


@inngest_client.create_function(
    fn_id="make-report",
    name="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,
)
async def make_report(ctx: inngest.Context, step: inngest.Step) -> dict[str, Any]:
    """Stage 2 & 3: Make report with 8-second slow work simulation & retry handling."""
    data = ctx.event.data or {}
    report_id = data.get("id")
    topic = data.get("topic", "general")

    # Step 1: Simulate the slow work (AI call, deep analytics, export)
    await step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))

    # Step 2: Build report and update data store
    async def build_report() -> dict[str, Any]:
        # Stage 3 test condition: fail trigger for watching retries
        if topic == "fail":
            update_report(report_id, status="failed", error="The report oven is broken!")
            raise RuntimeError("The report oven is broken!")

        result_content = (
            f"Comprehensive analysis and data aggregation for topic '{topic}'. "
            f"Generated at {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}."
        )

        # Update in-memory storage status
        record = update_report(report_id, status="done", result=result_content)

        # Optional extra: write to outbox/<id>.txt
        try:
            outbox_dir = os.path.join(os.path.dirname(__file__), "..", "outbox")
            os.makedirs(outbox_dir, exist_ok=True)
            outbox_path = os.path.join(outbox_dir, f"{report_id}.txt")
            with open(outbox_path, "w", encoding="utf-8") as f:
                f.write(f"Report ID: {report_id}\nTopic: {topic}\nResult: {result_content}\n")
        except Exception as e:
            logger.warning(f"Could not write outbox file: {e}")

        return {
            "id": report_id,
            "topic": topic,
            "status": "done",
            "result": result_content,
        }

    return await step.run("build-report", build_report)


@inngest_client.create_function(
    fn_id="heartbeat",
    name="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat(ctx: inngest.Context, step: inngest.Step) -> dict[str, Any]:
    """Stage 4: Periodic cron heartbeat logging report counts every minute."""
    async def log_summary() -> dict[str, Any]:
        summary = get_summary()
        msg = (
            f"[CRON HEARTBEAT] Reports summary -> "
            f"Pending: {summary.get('pending', 0)} | "
            f"Done: {summary.get('done', 0)} | "
            f"Failed: {summary.get('failed', 0)} | "
            f"Total: {summary.get('total', 0)}"
        )
        print(msg)
        logger.info(msg)
        return summary

    return await step.run("log-summary", log_summary)
