"""
Performance and large-scale tests for Beque.

Tests handling of tens of thousands of elements, FIFO ordering, and performance characteristics.
"""

import asyncio
import gc
import os
import random
import time
from collections import deque
from unittest.mock import AsyncMock

import psutil

from beque import Beque


class TestBequePerformance:
    """Test performance characteristics with large data sets."""

    async def test_large_scale_fifo_ordering_10k(self):
        """Test FIFO ordering with 10,000 elements."""
        processed_items = []
        processing_lock = asyncio.Lock()

        async def ordered_handler(batch):
            async with processing_lock:
                processed_items.extend(batch)

        num_items = 10_000

        async with Beque(
            on_flush=ordered_handler,
            max_batch_size=100,
            flush_interval=0.1,
        ) as beque:
            # Add items with clear ordering
            start_time = time.monotonic()
            for i in range(num_items):
                await beque.add(f"item_{i:05d}")

                # Occasional yield to prevent blocking
                if i % 1000 == 0:
                    await asyncio.sleep(0)

            add_time = time.monotonic() - start_time
            print(
                f"Added {num_items} items in {add_time:.2f}s ({num_items / add_time:.0f} items/s)"
            )

            # Wait for all processing to complete
            await asyncio.sleep(2.0)

        # Verify all items processed
        assert len(processed_items) == num_items

        # Verify FIFO order maintained
        for i, item in enumerate(processed_items):
            expected = f"item_{i:05d}"
            assert item == expected, (
                f"Order violation at index {i}: expected {expected}, got {item}"
            )

    async def test_large_scale_fifo_ordering_50k(self):
        """Test FIFO ordering with 50,000 elements."""
        processed_items = deque()  # Use deque for efficient append
        processing_lock = asyncio.Lock()

        async def ordered_handler(batch):
            async with processing_lock:
                processed_items.extend(batch)

        num_items = 50_000

        async with Beque(
            on_flush=ordered_handler,
            max_batch_size=500,  # Larger batches for efficiency
            flush_interval=0.2,
        ) as beque:
            start_time = time.monotonic()

            # Add items in chunks to test batch operations
            chunk_size = 100
            for chunk_start in range(0, num_items, chunk_size):
                chunk_end = min(chunk_start + chunk_size, num_items)
                chunk_items = [f"item_{i:06d}" for i in range(chunk_start, chunk_end)]
                await beque.add_many(chunk_items)

                # Yield occasionally
                if chunk_start % 10000 == 0:
                    await asyncio.sleep(0)

            add_time = time.monotonic() - start_time
            print(
                f"Added {num_items} items in {add_time:.2f}s ({num_items / add_time:.0f} items/s)"
            )

            # Wait for processing
            await asyncio.sleep(5.0)

        assert len(processed_items) == num_items

        # Sample check FIFO order (checking all 50k would be slow in CI)
        sample_indices = random.sample(range(num_items), min(1000, num_items))
        for i in sorted(sample_indices):
            expected = f"item_{i:06d}"
            actual = processed_items[i]
            assert actual == expected, (
                f"Order violation at index {i}: expected {expected}, got {actual}"
            )

    async def test_concurrent_large_scale_fifo(self):
        """Test FIFO ordering with concurrent producers at scale."""
        processed_items = []
        processing_lock = asyncio.Lock()

        async def concurrent_handler(batch):
            async with processing_lock:
                processed_items.extend(batch)

        async with Beque(
            on_flush=concurrent_handler,
            max_batch_size=200,
            flush_interval=0.1,
        ) as beque:

            async def producer(producer_id, item_count):
                items_to_add = []
                for i in range(item_count):
                    items_to_add.append(f"p{producer_id:02d}_i{i:04d}")

                # Add in chunks for efficiency
                chunk_size = 50
                for chunk_start in range(0, len(items_to_add), chunk_size):
                    chunk = items_to_add[chunk_start : chunk_start + chunk_size]
                    await beque.add_many(chunk)
                    await asyncio.sleep(0)  # Yield

            num_producers = 20
            items_per_producer = 500
            total_items = num_producers * items_per_producer

            start_time = time.monotonic()

            # Run concurrent producers
            await asyncio.gather(
                *[producer(pid, items_per_producer) for pid in range(num_producers)]
            )

            add_time = time.monotonic() - start_time
            print(f"Concurrent add of {total_items} items in {add_time:.2f}s")

            # Wait for processing
            await asyncio.sleep(3.0)

        assert len(processed_items) == total_items

        # Verify that items from each producer maintain their internal order
        producer_items = {}
        for item in processed_items:
            producer_id = item.split("_")[0]
            if producer_id not in producer_items:
                producer_items[producer_id] = []
            producer_items[producer_id].append(item)

        # Check each producer's items are in order
        for producer_id, items in producer_items.items():
            for i, item in enumerate(items):
                expected = f"{producer_id}_i{i:04d}"
                assert item == expected

    async def test_memory_efficiency_large_queue(self):
        """Test memory usage with large queues."""
        processed_count = 0

        async def memory_test_handler(batch):
            nonlocal processed_count
            processed_count += len(batch)
            # Add small delay to let queue build up
            await asyncio.sleep(0.01)

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        async with Beque(
            on_flush=memory_test_handler,
            max_batch_size=1000,  # Large batches
            flush_interval=0.5,  # Slower flushing to build queue
        ) as beque:
            # Add many items quickly to build up queue
            num_items = 25_000
            for i in range(num_items):
                # Use varied size strings to test memory usage
                item_data = f"memory_test_item_{i:06d}" + "x" * (i % 100)
                await beque.add(item_data)

                # Check memory periodically
                if i % 5000 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_increase = current_memory - initial_memory
                    print(
                        f"Items {i}: Queue size {beque.stats['queued']}, Memory: +{memory_increase:.1f}MB"
                    )

                    # Memory shouldn't grow unboundedly
                    assert memory_increase < 500, (
                        f"Memory usage too high: {memory_increase:.1f}MB"
                    )

                # Yield occasionally
                if i % 1000 == 0:
                    await asyncio.sleep(0)

        # Wait for final processing
        await asyncio.sleep(2.0)

        final_memory = process.memory_info().rss / 1024 / 1024
        final_increase = final_memory - initial_memory
        print(f"Final memory increase: {final_increase:.1f}MB")

        assert processed_count == num_items

        # Force garbage collection
        gc.collect()
        await asyncio.sleep(0.1)

    async def test_high_throughput_performance(self):
        """Test throughput with optimized settings."""
        processed_batches = []
        total_items = 0

        async def throughput_handler(batch):
            nonlocal total_items
            processed_batches.append(len(batch))
            total_items += len(batch)

        num_items = 20_000

        async with Beque(
            on_flush=throughput_handler,
            max_batch_size=1000,  # Large batches for throughput
            flush_interval=0.05,  # Fast flushing
        ) as beque:
            start_time = time.monotonic()

            # Add items as fast as possible
            for i in range(0, num_items, 100):
                chunk = [
                    f"throughput_item_{j}" for j in range(i, min(i + 100, num_items))
                ]
                await beque.add_many(chunk)

            add_time = time.monotonic() - start_time

            # Wait for processing
            await asyncio.sleep(1.0)

            process_time = time.monotonic() - start_time

        print(f"Throughput test: {num_items} items")
        print(f"Add time: {add_time:.3f}s ({num_items / add_time:.0f} items/s)")
        print(
            f"Total time: {process_time:.3f}s ({total_items / process_time:.0f} items/s)"
        )
        print(f"Batches processed: {len(processed_batches)}")

        assert total_items == num_items
        assert (
            len(processed_batches) < num_items / 10
        )  # Should use batching efficiently

    async def test_burst_handling_performance(self):
        """Test performance under bursty load patterns."""
        processed_items = []

        async def burst_handler(batch):
            processed_items.extend(batch)
            # Simulate realistic processing time
            await asyncio.sleep(len(batch) * 0.0001)  # 0.1ms per item

        async with Beque(
            on_flush=burst_handler,
            max_batch_size=250,
            flush_interval=0.1,
        ) as beque:
            total_items = 0

            # Simulate burst patterns
            for burst in range(5):
                print(f"Starting burst {burst + 1}")
                burst_start = time.monotonic()

                # Large burst of items
                burst_size = 3000
                for i in range(burst_size):
                    await beque.add(f"burst_{burst}_item_{i}")
                    total_items += 1

                burst_add_time = time.monotonic() - burst_start
                print(
                    f"Burst {burst + 1}: Added {burst_size} items in {burst_add_time:.2f}s"
                )

                # Quiet period
                await asyncio.sleep(0.2)

            # Wait for final processing
            await asyncio.sleep(2.0)

        assert len(processed_items) == total_items

        # Verify items from each burst maintain order within burst
        for burst in range(5):
            burst_items = [
                item for item in processed_items if item.startswith(f"burst_{burst}_")
            ]
            for i, item in enumerate(burst_items):
                expected = f"burst_{burst}_item_{i}"
                assert item == expected

    async def test_variable_item_size_performance(self):
        """Test performance with variable-sized items."""
        processed_sizes = []

        async def variable_size_handler(batch):
            batch_size = sum(len(str(item)) for item in batch)
            processed_sizes.append(batch_size)

        async with Beque(
            on_flush=variable_size_handler,
            max_batch_size=100,
            flush_interval=0.1,
        ) as beque:
            # Add items of varying sizes
            for i in range(5000):
                # Create items with sizes from 10 to 1000 characters
                item_size = 10 + (i % 990)
                item = f"item_{i:05d}" + "x" * item_size
                await beque.add(item)

                if i % 1000 == 0:
                    await asyncio.sleep(0)

            await asyncio.sleep(1.0)

        total_batches = len(processed_sizes)
        avg_batch_size = (
            sum(processed_sizes) / total_batches if total_batches > 0 else 0
        )

        print(
            f"Variable size test: {total_batches} batches, avg batch size: {avg_batch_size:.0f} chars"
        )
        assert total_batches > 0


class TestBequeLargeBatchBehavior:
    """Test behavior with very large batches."""

    async def test_single_large_batch_processing(self):
        """Test processing a single very large batch."""
        processed_items = []

        async def large_batch_handler(batch):
            processed_items.extend(batch)
            # Simulate processing time proportional to batch size
            await asyncio.sleep(len(batch) * 0.00001)

        large_batch_size = 10_000

        async with Beque(
            on_flush=large_batch_handler,
            max_batch_size=large_batch_size,
            flush_interval=1.0,
        ) as beque:
            start_time = time.monotonic()

            # Add exactly the batch size to trigger single large flush
            items = [f"large_batch_item_{i:06d}" for i in range(large_batch_size)]
            await beque.add_many(items)

            add_time = time.monotonic() - start_time

            # Wait for processing
            await asyncio.sleep(2.0)

            total_time = time.monotonic() - start_time

        print(f"Large batch test: {large_batch_size} items in single batch")
        print(f"Add time: {add_time:.3f}s, Total time: {total_time:.3f}s")

        assert len(processed_items) == large_batch_size

        # Verify order in the large batch
        for i in range(min(1000, large_batch_size)):  # Sample check
            expected = f"large_batch_item_{i:06d}"
            assert processed_items[i] == expected

    async def test_multiple_large_batches(self):
        """Test processing multiple consecutive large batches."""
        batch_info = []

        async def multi_large_batch_handler(batch):
            batch_info.append(
                {
                    "size": len(batch),
                    "first_item": batch[0] if batch else None,
                    "last_item": batch[-1] if batch else None,
                    "timestamp": time.monotonic(),
                }
            )

        batch_size = 5_000
        num_batches = 10

        async with Beque(
            on_flush=multi_large_batch_handler,
            max_batch_size=batch_size,
            flush_interval=0.5,
        ) as beque:
            start_time = time.monotonic()

            # Add items to create multiple large batches
            for batch_num in range(num_batches):
                batch_items = [
                    f"batch_{batch_num:02d}_item_{i:05d}" for i in range(batch_size)
                ]
                await beque.add_many(batch_items)

                # Small delay between batches
                await asyncio.sleep(0.01)

            add_time = time.monotonic() - start_time

            # Wait for all processing
            await asyncio.sleep(3.0)

            total_time = time.monotonic() - start_time

        print(
            f"Multiple large batches: {num_batches} batches of {batch_size} items each"
        )
        print(f"Add time: {add_time:.2f}s, Total time: {total_time:.2f}s")
        print(f"Processed {len(batch_info)} batches")

        assert len(batch_info) == num_batches

        # Verify each batch was the correct size
        for i, info in enumerate(batch_info):
            assert info["size"] == batch_size
            expected_first = f"batch_{i:02d}_item_00000"
            expected_last = f"batch_{i:02d}_item_{batch_size - 1:05d}"
            assert info["first_item"] == expected_first
            assert info["last_item"] == expected_last

    async def test_mixed_small_and_large_batches(self):
        """Test handling mix of small frequent items and large batch additions."""
        processed_batches = []

        async def mixed_batch_handler(batch):
            processed_batches.append(
                {
                    "size": len(batch),
                    "items": batch.copy(),
                    "timestamp": time.monotonic(),
                }
            )

        async with Beque(
            on_flush=mixed_batch_handler,
            max_batch_size=1000,
            flush_interval=0.1,
        ) as beque:

            async def small_item_producer():
                # Add small items continuously
                for i in range(500):
                    await beque.add(f"small_item_{i:04d}")
                    await asyncio.sleep(0.001)  # 1ms between items

            async def large_batch_producer():
                # Add large batches occasionally
                await asyncio.sleep(0.1)  # Start after small items begin

                for batch_num in range(3):
                    large_batch = [
                        f"large_batch_{batch_num}_item_{i:04d}" for i in range(800)
                    ]
                    await beque.add_many(large_batch)
                    await asyncio.sleep(0.05)  # Gap between large batches

            # Run both producers concurrently
            await asyncio.gather(small_item_producer(), large_batch_producer())

            # Wait for processing
            await asyncio.sleep(1.0)

        total_items_processed = sum(batch["size"] for batch in processed_batches)
        expected_total = 500 + (3 * 800)  # small items + large batches

        assert total_items_processed == expected_total

        # Verify we got a mix of batch sizes
        batch_sizes = [batch["size"] for batch in processed_batches]
        has_small_batches = any(size < 100 for size in batch_sizes)
        has_large_batches = any(size > 500 for size in batch_sizes)

        assert has_small_batches and has_large_batches


class TestBequeStressScenarios:
    """Stress tests for extreme conditions."""

    async def test_rapid_start_stop_cycles(self):
        """Test rapid start/stop cycles don't cause issues."""
        handler = AsyncMock()

        for cycle in range(20):
            beque = Beque(on_flush=handler, max_batch_size=10)

            await beque.start()

            # Add some items quickly
            for i in range(5):
                await beque.add(f"cycle_{cycle}_item_{i}")

            await beque.stop()

            # Brief pause
            await asyncio.sleep(0.001)

        # Should have processed items from all cycles
        assert handler.call_count >= 10  # At least some calls

    async def test_extreme_batch_size_ratios(self):
        """Test with extreme ratios of batch size to item count."""
        test_cases = [
            (1, 1000),  # Very small batches, many items
            (10000, 50),  # Very large batches, few items
            (100, 100000),  # Medium batches, very many items
        ]

        for batch_size, item_count in test_cases:
            processed_count = 0

            async def ratio_test_handler(batch):
                nonlocal processed_count
                processed_count += len(batch)

            print(f"Testing batch_size={batch_size}, item_count={item_count}")

            start_time = time.monotonic()

            async with Beque(
                on_flush=ratio_test_handler,
                max_batch_size=batch_size,
                flush_interval=0.1,
            ) as beque:
                # Add items efficiently
                chunk_size = min(1000, item_count // 10)
                for start_idx in range(0, item_count, chunk_size):
                    end_idx = min(start_idx + chunk_size, item_count)
                    chunk = [f"ratio_item_{i}" for i in range(start_idx, end_idx)]
                    await beque.add_many(chunk)

                    # Yield periodically
                    if start_idx % 10000 == 0:
                        await asyncio.sleep(0)

                # Wait for processing
                await asyncio.sleep(max(1.0, item_count / 10000))

            duration = time.monotonic() - start_time
            print(
                f"  Completed in {duration:.2f}s, processed {processed_count}/{item_count} items"
            )

            assert processed_count == item_count

    async def test_queue_buildup_and_drainage(self):
        """Test queue building up and then draining."""
        processed_items = []
        processing_enabled = False

        async def drainage_test_handler(batch):
            if processing_enabled:
                processed_items.extend(batch)
            else:
                # When processing disabled, items get requeued
                raise Exception("Processing temporarily disabled")

        async with Beque(
            on_flush=drainage_test_handler,
            max_batch_size=100,
            flush_interval=0.05,
        ) as beque:
            # Phase 1: Add items while processing is disabled (builds up queue)
            print("Phase 1: Building up queue")
            for i in range(2000):
                await beque.add(f"buildup_item_{i:05d}")
                if i % 500 == 0:
                    await asyncio.sleep(0)

            # Let it try to process (and fail) for a bit
            await asyncio.sleep(0.5)

            buildup_stats = beque.stats
            print(
                f"Queue buildup: {buildup_stats['queued']} items, {buildup_stats['failures']} failures"
            )

            # Phase 2: Enable processing and let it drain
            print("Phase 2: Draining queue")
            processing_enabled = True

            # Wait for queue to drain
            drain_start = time.monotonic()
            while beque.stats["queued"] > 0:
                await asyncio.sleep(0.1)
                if time.monotonic() - drain_start > 10:  # Timeout
                    break

            drain_time = time.monotonic() - drain_start
            final_stats = beque.stats

            print(f"Queue drained in {drain_time:.2f}s")
            print(
                f"Final stats: {final_stats['items']} items processed, {final_stats['queued']} queued"
            )

        # Should have processed all items eventually
        assert len(processed_items) == 2000

        # Verify FIFO order maintained despite the processing interruption
        for i, item in enumerate(processed_items):
            expected = f"buildup_item_{i:05d}"
            assert item == expected, (
                f"Order violation at {i}: expected {expected}, got {item}"
            )

    async def test_long_running_stability(self):
        """Test stability over a longer period with varied load."""
        processed_count = 0
        error_count = 0

        async def stability_handler(batch):
            nonlocal processed_count, error_count
            try:
                processed_count += len(batch)
                # Occasionally simulate processing errors (5% chance)
                if random.random() < 0.05:
                    raise Exception("Random processing error")
                await asyncio.sleep(0.001)  # Small processing delay
            except Exception:
                error_count += 1
                raise

        async with Beque(
            on_flush=stability_handler,
            max_batch_size=50,
            flush_interval=0.2,
        ) as beque:
            start_time = time.monotonic()
            total_added = 0

            # Run for several seconds with varying load
            while time.monotonic() - start_time < 3.0:  # 3 second test
                # Vary the addition rate
                current_time = time.monotonic() - start_time
                if current_time % 1.0 < 0.5:  # High load for first half of each second
                    burst_size = random.randint(10, 50)
                    items = [
                        f"stability_item_{total_added + i}" for i in range(burst_size)
                    ]
                    await beque.add_many(items)
                    total_added += burst_size
                else:  # Low load for second half
                    await beque.add(f"stability_item_{total_added}")
                    total_added += 1
                    await asyncio.sleep(0.01)

                # Occasional stats check
                if total_added % 1000 == 0:
                    stats = beque.stats
                    print(
                        f"Added {total_added}, processed {processed_count}, queued {stats['queued']}"
                    )

            # Wait for final processing
            await asyncio.sleep(1.0)

        final_stats = beque.stats
        print("Stability test completed:")
        print(f"  Total added: {total_added}")
        print(f"  Total processed: {processed_count}")
        print(f"  Processing errors: {error_count}")
        print(f"  Final queue size: {final_stats['queued']}")

        # Should process most items (allowing for some failures)
        processed_ratio = processed_count / total_added
        assert processed_ratio > 0.8  # At least 80% success rate
