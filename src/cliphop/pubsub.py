"""In-Process-Pub/Sub für Live-Updates (ein Prozess, ein Worker)."""

from __future__ import annotations

import asyncio


class Broadcaster:
    """Verteilt Nachrichten an alle offenen SSE-Streams."""

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self._subscribers.discard(queue)

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)

    def publish(self, payload: str) -> None:
        for queue in list(self._subscribers):
            queue.put_nowait(payload)
