"""Development CLI — run pipeline stages without waiting for the scheduler.

Usage:
    uv run python cli.py collect
    uv run python cli.py analyze
    uv run python cli.py generate-digest
    uv run python cli.py send-digest
    uv run python cli.py run-daily
"""

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime

from core.database import SessionLocal
from core.logging import setup_logging
from modules.ai.service import analyze_pending, ensure_user
from modules.digest.generator import generate_digest
from modules.scheduler.pipeline import collect_stage, digest_and_send


async def cmd_collect() -> None:
    async with SessionLocal() as db:
        stats = await collect_stage(db)
    print(json.dumps(stats, indent=2, default=str))


async def cmd_analyze() -> None:
    async with SessionLocal() as db:
        user = await ensure_user(db)
        count = await analyze_pending(db, user.id)
    print(json.dumps({"analyzed": count}))


async def cmd_generate_digest() -> None:
    async with SessionLocal() as db:
        user = await ensure_user(db)
        today = datetime.now(UTC).date()
        digest = await generate_digest(db, user.id, today)
    print(json.dumps({"digest_id": str(digest.id), "items": len(digest.items)}))


async def cmd_send_digest() -> None:
    async with SessionLocal() as db:
        result = await digest_and_send(db, send=True)
    print(json.dumps(result))


async def cmd_run_daily() -> None:
    from modules.scheduler.pipeline import run_daily_pipeline

    result = await run_daily_pipeline()
    print(json.dumps(result, indent=2, default=str))


COMMANDS = {
    "collect": cmd_collect,
    "analyze": cmd_analyze,
    "generate-digest": cmd_generate_digest,
    "send-digest": cmd_send_digest,
    "run-daily": cmd_run_daily,
}


def main() -> int:
    setup_logging()
    parser = argparse.ArgumentParser(description="personal-tech-radar pipeline CLI")
    parser.add_argument("command", choices=sorted(COMMANDS))
    args = parser.parse_args()
    asyncio.run(COMMANDS[args.command]())
    return 0


if __name__ == "__main__":
    sys.exit(main())
