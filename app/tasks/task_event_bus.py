"""
A tiny in-process pub/sub: routes publish events,
every connected WebSocket / SSE client gets its own asyncio.Queue.
"""

import asyncio
from collections.abc import AsyncIterator, Iterator
from contextlib import contextmanager, suppress

from app.tasks.task_event import TaskEvent


class TaskEventBus:

    def __init__(self, buffer_size: int = 64) -> None:
        self._buffer_size = buffer_size
        self._subscribers: set[asyncio.Queue[TaskEvent]] = set()

    async def publish(self, event: TaskEvent) -> None:
        for queue in tuple(self._subscribers):
            # A client that does not keep up simply misses events instead of blocking everyone.
            with suppress(asyncio.QueueFull):
                queue.put_nowait(event)

    @contextmanager
    def subscribe(self) -> Iterator[AsyncIterator[TaskEvent]]:
        """
        Usage:  with bus.subscribe() as events:
                    async for event in events: ...
        The subscription is active as soon as the `with` block is entered.
        """
        queue: asyncio.Queue[TaskEvent] = asyncio.Queue(maxsize=self._buffer_size)
        self._subscribers.add(queue)
        try:
            yield self._drain(queue)
        finally:
            self._subscribers.discard(queue)

    @staticmethod
    async def _drain(queue: asyncio.Queue[TaskEvent]) -> AsyncIterator[TaskEvent]:
        while True:
            yield await queue.get()
