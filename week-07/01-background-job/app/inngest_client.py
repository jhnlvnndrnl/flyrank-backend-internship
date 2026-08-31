"""Inngest Client Setup."""

import inngest
from .config import INNGEST_DEV, INNGEST_EVENT_KEY, INNGEST_SIGNING_KEY

inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=not INNGEST_DEV,
    event_key=INNGEST_EVENT_KEY,
    signing_key=INNGEST_SIGNING_KEY,
)
