"""Notification abstraction — backend must not be coupled to Telegram (GOAL.md §6)."""

import abc


class NotificationProvider(abc.ABC):
    channel: str

    @abc.abstractmethod
    async def send(self, *, text: str, chat_id: str) -> bool: ...
