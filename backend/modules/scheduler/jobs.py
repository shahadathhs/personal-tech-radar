"""APScheduler setup — one daily job, safe to rerun (GOAL.md §36, §37)."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.config import settings
from core.redis_client import client as redis_client
from modules.scheduler.pipeline import run_daily_pipeline

logger = logging.getLogger("radar.scheduler.jobs")

scheduler = AsyncIOScheduler(timezone=settings.timezone)
LOCK_KEY = "radar:daily-pipeline-lock"
LOCK_TTL_SECONDS = 3600


def _parse_time(raw: str) -> tuple[int, int]:
    try:
        hour, minute = raw.split(":", 1)
        return int(hour), int(minute)
    except ValueError:
        return 19, 0


async def daily_job() -> None:
    """Run the pipeline under a Redis lock so overlapping runs are impossible."""
    got_lock = await redis_client.set(
        LOCK_KEY, datetime.now().isoformat(), nx=True, ex=LOCK_TTL_SECONDS
    )
    if not got_lock:
        logger.info("Daily pipeline already running — skipping")
        return
    try:
        await run_daily_pipeline()
    except Exception:
        logger.exception("Daily pipeline failed")
    finally:
        await redis_client.delete(LOCK_KEY)


def start_scheduler() -> None:
    hour, minute = _parse_time(settings.digest_time)
    tz = ZoneInfo(settings.timezone)
    scheduler.add_job(
        daily_job,
        CronTrigger(hour=hour, minute=minute, timezone=tz),
        id="daily-digest",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started: daily at %s %s", settings.digest_time, settings.timezone)


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
