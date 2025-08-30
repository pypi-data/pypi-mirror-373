# Beque - Asynchronous In-Memory Batch Queue Processor

**Beque** (pronounced "Beck") is a lightweight, high-performance Python library for asynchronous batch processing. It accumulates items in memory and flushes them to an async sink when either:

* `max_batch_size` items are queued, or
* `flush_interval` seconds have passed since the last successful flush

Flushing is serialized and items are never lost: on failure, the batch is re-queued in original order.

## Features

* **Async/await support**: Built for modern Python asyncio applications
* **Batch processing**: Efficiently processes items in configurable batches
* **Time-based flushing**: Automatic flushing based on configurable intervals
* **Error resilience**: Failed batches are re-queued and retried
* **Thread-safe**: Safe for concurrent access across async tasks
* **Generic typing**: Full type safety with Python's generic typing system
* **Comprehensive stats**: Built-in statistics and monitoring
* **Zero dependencies**: No external dependencies required

## Installation

```bash
pip install beque
```

## Quick Start

```python
import asyncio
from beque import Beque

async def process_batch(items):
    """Your async batch processing function."""
    print(f"Processing {len(items)} items: {items}")
    # Simulate async work (database write, API call, etc.)
    await asyncio.sleep(0.1)

async def main():
    # Create a Beque that flushes every 5 items or every 10 seconds
    async with Beque(
        on_flush=process_batch, 
        max_batch_size=5, 
        flush_interval=10.0
    ) as queue:
        
        # Add items to the queue
        for i in range(12):
            await queue.add(f"item-{i}")
            await asyncio.sleep(0.5)
        
        # Items are automatically flushed in batches
        # Final flush happens when exiting the context manager

asyncio.run(main())
```

## API Reference

### Beque Class

```python
class Beque(Generic[T]):
    def __init__(
        self,
        *,
        on_flush: Callable[[List[T]], Awaitable[None]],
        max_batch_size: int = 100,
        flush_interval: float = 10.0,
        name: str = "Beque",
        logger: logging.Logger = None,
    )
```

**Parameters:**

* `on_flush`: Async function that processes batches of items
* `max_batch_size`: Maximum items in a batch before auto-flush (default: 100)
* `flush_interval`: Seconds between time-based flushes (default: 10.0)
* `name`: Name for logging and identification (default: "Beque")
* `logger`: Custom logger instance (optional)

### Methods

#### `async add(item: T) -> None`

Add a single item to the queue.

#### `async add_many(items: List[T]) -> None`

Add multiple items to the queue atomically.

#### `async flush(*, force: bool = True) -> None`

Manually trigger a flush. If `force=True`, flushes all queued items.

#### `stats -> dict`

Get current statistics:

```python
{
    "flushes": int,      # Total successful flushes
    "items": int,        # Total items processed  
    "failures": int,     # Total flush failures
    "queued": int,       # Current items in queue
    "last_flush_time": float,  # Timestamp of last flush
    "running": bool      # Whether queue is active
}
```

### Context Manager Usage

Beque is designed to be used as an async context manager:

```python
async with Beque(on_flush=handler) as queue:
    await queue.add(item)
    # Automatic cleanup and final flush on exit
```

Or manually:

```python
queue = Beque(on_flush=handler)
await queue.start()
try:
    await queue.add(item)
finally:
    await queue.stop()  # Ensures final flush
```

## Advanced Examples

### Database Batch Inserts

```python
import asyncio
from beque import Beque

class DatabaseWriter:
    async def write_users(self, user_batch):
        # Simulate batch database insert
        print(f"INSERT INTO users VALUES {user_batch}")
        await asyncio.sleep(0.1)  # Simulated I/O

async def main():
    db = DatabaseWriter()
    
    async with Beque(
        on_flush=db.write_users,
        max_batch_size=10,
        flush_interval=5.0
    ) as user_queue:
        
        # Simulate receiving user data
        for i in range(25):
            user_data = {"id": i, "name": f"user-{i}"}
            await user_queue.add(user_data)
            await asyncio.sleep(0.2)

asyncio.run(main())
```

### Error Handling and Recovery

```python
import asyncio
import random
from beque import Beque

async def flaky_processor(batch):
    """Processor that occasionally fails."""
    if random.random() < 0.3:  # 30% failure rate
        raise Exception("Processing failed!")
    
    print(f"Successfully processed: {batch}")
    await asyncio.sleep(0.1)

async def main():
    async with Beque(
        on_flush=flaky_processor,
        max_batch_size=3,
        flush_interval=2.0
    ) as queue:
        
        for i in range(10):
            await queue.add(f"task-{i}")
            await asyncio.sleep(0.5)
        
        # Check stats to see failure/retry information
        print("Final stats:", queue.stats)

asyncio.run(main())
```

### Multiple Concurrent Producers

```python
import asyncio
from beque import Beque

async def log_processor(batch):
    print(f"Logged {len(batch)} events: {batch}")
    await asyncio.sleep(0.05)

async def producer(queue, producer_id):
    """Simulate concurrent event producers."""
    for i in range(10):
        event = f"producer-{producer_id}-event-{i}"
        await queue.add(event)
        await asyncio.sleep(0.1)

async def main():
    async with Beque(
        on_flush=log_processor,
        max_batch_size=5,
        flush_interval=1.0
    ) as event_queue:
        
        # Start multiple concurrent producers
        await asyncio.gather(
            producer(event_queue, 1),
            producer(event_queue, 2),
            producer(event_queue, 3),
        )

asyncio.run(main())
```

## Type Safety

Beque is fully typed and supports generic type parameters:

```python
from beque import Beque
from typing import Dict

async def process_dicts(batch: List[Dict[str, int]]) -> None:
    for item in batch:
        print(f"Processing: {item}")

# Type-safe queue for dictionaries
queue: Beque[Dict[str, int]] = Beque(on_flush=process_dicts)
```

## Performance Characteristics

* **Memory**: O(n) where n is the number of queued items
* **Throughput**: Optimized for high-frequency additions with batched processing
* **Latency**: Configurable via `flush_interval` and `max_batch_size`
* **Concurrency**: Thread-safe with asyncio locks, supports many concurrent producers

## Error Handling

Beque provides robust error handling:

1. **Flush failures**: Batches are re-queued in original order
2. **Automatic retry**: Failed batches will be retried on next flush opportunity
3. **Graceful shutdown**: Context manager ensures final flush even on exceptions
4. **Statistics tracking**: Monitor success/failure rates via `stats` property

## Logging

Beque provides structured logging at various levels:

* **INFO**: Start/stop events with configuration
* **DEBUG**: Individual flush operations
* **ERROR**: Flush failures with full context

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_app.queue")

async with Beque(on_flush=handler, logger=logger) as queue:
    # Custom logger will be used for all queue events
    pass
```

## Requirements

* Python 3.8+
* No external dependencies

## License

MIT License - see LICENSE file for details.
