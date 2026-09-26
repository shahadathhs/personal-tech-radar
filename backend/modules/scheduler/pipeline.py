"""Daily pipeline orchestration — each stage independently executable (GOAL.md §36).

collect → normalize → dedupe → analyze → rank → generate_digest → send
"""

import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import SessionLocal
from models import Digest, Notification, NotificationStatus
from modules.ai.service import analyze_pending, ensure_user
from modules.digest.formatter import format_telegram
from modules.digest.generator import generate_digest, load_digest_items
from modules.ingestion.collector import ensure_seed_sources, run_collection
from modules.notifications.telegram import send_digest_message

logger = logging.getLogger("radar.scheduler.pipeline")


async def collect_stage(db: AsyncSession) -> dict:
    await ensure_seed_sources(db)
    stats = await run_collection(db)
    return stats


async def digest_and_send(db: AsyncSession, *, send: bool) -> dict:
    user = await ensure_user(db)
    today = datetime.now(UTC).date()
    digest: Digest = await generate_digest(db, user.id, today)

    rows = await load_digest_items(db, digest.id)
    text = format_telegram(
        digest_date=digest.digest_date.isoformat(),
        reading_time=digest.reading_time_minutes,
        rows=rows,
    )

    sent = False
    if send:
        sent = await send_digest_message(text)
        notification = Notification(
            user_id=user.id,
            digest_id=digest.id,
            channel="telegram",
            status=NotificationStatus.sent.value if sent else NotificationStatus.failed.value,
            sent_at=datetime.now(UTC) if sent else None,
        )
        db.add(notification)
        if sent:
            digest.status = "sent"
            digest.sent_at = datetime.now(UTC)
        await db.commit()

    logger.info("Digest %s: generated, sent=%s", digest.id, sent)
    return {"digest_id": str(digest.id), "items": len(rows), "sent": sent}


async def run_daily_pipeline() -> dict:
    """Full end-to-end run. Each stage isolated; later stages need earlier output."""
    logger.info("Daily pipeline started")
    async with SessionLocal() as db:
        stats = await collect_stage(db)
    async with SessionLocal() as db:
        analyzed = await analyze_pending(db, user_id=(await ensure_user(db)).id)
    async with SessionLocal() as db:
        result = await digest_and_send(db, send=True)
    logger.info("Daily pipeline finished: collected=%s analyzed=%d", stats, analyzed)
    return {**stats, "analyzed": analyzed, **result}
