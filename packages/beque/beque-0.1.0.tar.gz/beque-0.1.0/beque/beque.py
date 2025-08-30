"""
Beque - Asynchronous In-Memory Batch Queue Processor

Beque accumulates items in-memory and flushes them to an async sink when either:
• max_batch_size items are queued, or
• flush_interval seconds have passed since the last successful flush.

Flushing is serialized and items are never lost: on failure the batch
is re-queued in original order.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from typing import Awaitable, Callable, Deque, Generic, List, Optional, TypeVar

__version__ = "0.1.0"
__all__ = ["Beque"]

T = TypeVar("T")


class Beque(Generic[T]):
    """
    Beque (Batch Queue) accumulates items in-memory and flushes them to
    an async sink when either:
      • max_batch_size items are queued, or
      • flush_interval seconds have passed since the last successful flush.

    Flushing is serialized and items are never lost: on failure the batch
    is re-queued in original order.

    Use as an async context manager:

        async with Beque(on_flush=my_handler) as q:
            await q.add(item)
    """

    def __init__(
        self,
        *,
        on_flush: Callable[[List[T]], Awaitable[None]],
        max_batch_size: int = 100,
        flush_interval: float = 10.0,
        name: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        if max_batch_size < 1:
            raise ValueError("max_batch_size must be >= 1")
        if flush_interval <= 0:
            raise ValueError("flush_interval must be > 0")

        self._on_flush = on_flush
        self._max_batch_size = int(max_batch_size)
        self._flush_interval = float(flush_interval)

        self._name = name or "Beque"
        self._logger = logger or logging.getLogger(self._name)

        self._queue: Deque[T] = deque()
        self._queue_lock = asyncio.Lock()
        self._consume_lock = asyncio.Lock()
        self._flush_event = asyncio.Event()

        self._task: Optional[asyncio.Task[None]] = None
        self._running = False
        self._last_flush_time: Optional[float] = None

        self._total_flushes = 0
        self._total_items = 0
        self._failed_flushes = 0

    async def start(self) -> None:
        """Start the background consumer loop."""
        if self._running:
            return
        self._running = True
        self._last_flush_time = time.monotonic()
        self._task = asyncio.create_task(self._run(), name=f"{self._name}-consumer")
        self._logger.info(
            "Started (max_batch_size=%d, flush_interval=%.2fs)",
            self._max_batch_size,
            self._flush_interval,
        )

    async def stop(self) -> None:
        """Stop the consumer and flush remaining items."""
        if not self._running:
            return
        self._running = False
        self._flush_event.set()
        if self._task:
            await self._task
            self._task = None
        await self.flush(force=True)
        self._logger.info(
            "Stopped (flushes=%d, items=%d, failures=%d)",
            self._total_flushes,
            self._total_items,
            self._failed_flushes,
        )

    async def __aenter__(self) -> Beque[T]:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.stop()

    async def add(self, item: T) -> None:
        """Enqueue a single item."""
        if not self._running:
            raise RuntimeError("Beque is not running")
        async with self._queue_lock:
            self._queue.append(item)
            if len(self._queue) >= self._max_batch_size:
                self._flush_event.set()

    async def add_many(self, items: List[T]) -> None:
        """Enqueue multiple items atomically."""
        if not items:
            return
        if not self._running:
            raise RuntimeError("Beque is not running")
        async with self._queue_lock:
            self._queue.extend(items)
            if len(self._queue) >= self._max_batch_size:
                self._flush_event.set()

    async def flush(self, *, force: bool = True) -> None:
        """Flush immediately (force=True flushes all items)."""
        await self._flush_if_needed(force=force)

    @property
    def stats(self) -> dict:
        """Get current queue statistics."""
        return {
            "flushes": self._total_flushes,
            "items": self._total_items,
            "failures": self._failed_flushes,
            "queued": len(self._queue),
            "last_flush_time": self._last_flush_time,
            "running": self._running,
        }

    async def _run(self) -> None:
        try:
            while self._running:
                now = time.monotonic()
                elapsed = now - (self._last_flush_time or now)
                timeout = max(0.0, self._flush_interval - elapsed)

                try:
                    await asyncio.wait_for(self._flush_event.wait(), timeout=timeout)
                    triggered_by_event = True
                except asyncio.TimeoutError:
                    triggered_by_event = False
                if triggered_by_event:
                    self._flush_event.clear()

                await self._flush_if_needed(force=not triggered_by_event)
        except Exception:
            self._logger.exception("Background consumer error")
        finally:
            await self._flush_if_needed(force=True)

    async def _flush_if_needed(self, *, force: bool) -> None:
        batch: List[T] = []
        async with self._queue_lock:
            if not self._queue:
                return
            if force:
                batch.extend(self._queue)
                self._queue.clear()
            elif len(self._queue) >= self._max_batch_size:
                for _ in range(self._max_batch_size):
                    batch.append(self._queue.popleft())
        if not batch:
            return

        try:
            async with self._consume_lock:
                await self._on_flush(batch)
            self._total_flushes += 1
            self._total_items += len(batch)
            self._last_flush_time = time.monotonic()
            self._logger.debug("Flushed %d items", len(batch))
        except Exception:
            self._failed_flushes += 1
            self._logger.exception("Flush failed, re-queuing %d items", len(batch))
            async with self._queue_lock:
                for item in reversed(batch):
                    self._queue.appendleft(item)
            await asyncio.sleep(0.5)
