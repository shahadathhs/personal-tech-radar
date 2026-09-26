"""Telegram provider via the Bot API (GOAL.md §6)."""

import logging

import httpx

from core.config import settings
from modules.notifications.base import NotificationProvider

logger = logging.getLogger("radar.notifications.telegram")
API = "https://api.telegram.org"


class TelegramProvider(NotificationProvider):
    channel = "telegram"

    async def send(self, *, text: str, chat_id: str) -> bool:
        if not settings.telegram_bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not configured — message not sent")
            return False
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{API}/bot{settings.telegram_bot_token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "disable_web_page_preview": True,
                },
            )
            if resp.status_code != 200:
                logger.error("Telegram send failed: %s %s", resp.status_code, resp.text[:300])
                return False
            return True


async def send_digest_message(text: str) -> bool:
    if not settings.telegram_chat_id:
        logger.warning("TELEGRAM_CHAT_ID not configured — message not sent")
        return False
    return await TelegramProvider().send(text=text, chat_id=settings.telegram_chat_id)
