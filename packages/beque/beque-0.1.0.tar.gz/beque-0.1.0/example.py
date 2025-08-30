#!/usr/bin/env python3
"""
Simple example demonstrating Beque usage.
"""

import asyncio
import logging

from beque import Beque

logging.basicConfig(level=logging.INFO)


async def fake_db(batch):
    """Simulate database batch insert with a delay."""
    await asyncio.sleep(0.1)
    print(f"DB wrote: {batch}")


async def main():
    """Run the example."""
    async with Beque(on_flush=fake_db, max_batch_size=5, flush_interval=3) as q:
        for i in range(12):
            await q.add(i)
            await asyncio.sleep(0.2)


if __name__ == "__main__":
    asyncio.run(main())
