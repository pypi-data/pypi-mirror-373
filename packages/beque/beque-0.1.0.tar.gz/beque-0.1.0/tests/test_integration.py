"""
Integration tests for Beque.

Tests error handling, recovery, concurrent operations, and real-world scenarios.
"""

import asyncio
import logging
import random
import time
from unittest.mock import AsyncMock

from beque import Beque


class TestBequeErrorHandling:
    """Test error handling and recovery."""

    async def test_flush_failure_requeues_items(self):
        """Test that failed flush re-queues items in original order."""
        handler = AsyncMock(side_effect=Exception("Flush failed"))

        async with Beque(
            on_flush=handler, max_batch_size=2, flush_interval=10.0
        ) as beque:
            await beque.add("item1")
            await beque.add("item2")

            # Give time for flush attempt and recovery
            await asyncio.sleep(0.6)  # Account for 0.5s sleep in error handling

            # Items should be back in queue
            stats = beque.stats
            assert stats["queued"] == 2
            assert stats["failures"] == 1
            assert stats["flushes"] == 0

            # Verify items are in correct order by checking queue directly
            items = list(beque._queue)
            assert items == ["item1", "item2"]

    async def test_multiple_flush_failures(self):
        """Test handling of multiple consecutive failures."""
        handler = AsyncMock(side_effect=Exception("Always fails"))

        async with Beque(
            on_flush=handler, max_batch_size=1, flush_interval=0.1
        ) as beque:
            await beque.add("item1")

            # Give time for multiple flush attempts
            await asyncio.sleep(0.8)

            stats = beque.stats
            assert stats["failures"] > 1
            assert stats["flushes"] == 0
            assert stats["queued"] == 1

    async def test_recovery_after_failure(self):
        """Test that queue recovers after handler is fixed."""
        call_count = 0

        async def flaky_handler(batch):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First call fails")

        async with Beque(
            on_flush=flaky_handler, max_batch_size=1, flush_interval=0.1
        ) as beque:
            await beque.add("item1")

            # Give time for failure and recovery
            await asyncio.sleep(0.8)

            stats = beque.stats
            # Should eventually succeed
            assert stats["flushes"] >= 1
            assert stats["failures"] >= 1

    async def test_partial_batch_failure_preserves_order(self):
        """Test that partial batch failures maintain FIFO order."""
        processed_items = []
        fail_next = True

        async def sometimes_failing_handler(batch):
            nonlocal fail_next
            if fail_next:
                fail_next = False
                raise Exception("Intentional failure")
            processed_items.extend(batch)

        async with Beque(
            on_flush=sometimes_failing_handler, max_batch_size=3, flush_interval=0.1
        ) as beque:
            # Add items that should maintain order
            for i in range(6):
                await beque.add(f"item{i}")

            # Wait for processing and recovery
            await asyncio.sleep(1.0)

        # Should eventually process all items in order
        expected_order = [f"item{i}" for i in range(6)]
        assert processed_items == expected_order

    async def test_error_logging(self, caplog):
        """Test that flush errors are logged."""
        handler = AsyncMock(side_effect=Exception("Test error"))
        custom_logger = logging.getLogger("test_error_beque")

        with caplog.at_level(logging.ERROR, logger="test_error_beque"):
            async with Beque(
                on_flush=handler,
                logger=custom_logger,
                max_batch_size=1,
            ) as beque:
                await beque.add("item")
                await asyncio.sleep(0.6)  # Wait for error handling

        # Should have logged the flush failure
        assert any("Flush failed" in record.message for record in caplog.records)

    async def test_handler_timeout_handling(self):
        """Test behavior when handler times out (takes too long)."""
        timeout_occurred = False

        async def slow_handler(batch):
            nonlocal timeout_occurred
            timeout_occurred = True
            await asyncio.sleep(2.0)  # Very slow handler
            return batch

        async with Beque(
            on_flush=slow_handler, max_batch_size=1, flush_interval=0.1
        ) as beque:
            await beque.add("item1")

            # Add more items while first is processing
            await asyncio.sleep(0.2)  # Let first start processing
            await beque.add("item2")

            # Items should queue up while handler is slow
            stats = beque.stats
            assert stats["queued"] >= 1  # Second item should be queued

            # Wait for processing to complete
            await asyncio.sleep(2.5)

        assert timeout_occurred

    async def test_exception_in_background_consumer(self):
        """Test handling of unexpected exceptions in background consumer."""
        processed_items = []
        exception_count = 0

        async def handler_with_background_exception(batch):
            nonlocal exception_count
            processed_items.extend(batch)

            # Simulate an exception that happens during background processing
            if len(processed_items) == 2 and exception_count == 0:
                exception_count += 1
                # This will be caught by the background consumer's exception handler
                raise Exception("Background consumer exception")

        # The queue should continue operating despite the exception
        async with Beque(
            on_flush=handler_with_background_exception,
            max_batch_size=1,
            flush_interval=0.1,
        ) as beque:
            await beque.add("item1")
            await beque.add("item2")
            await beque.add("item3")

            await asyncio.sleep(0.5)

        # Should process at least some items despite the exception
        assert len(processed_items) >= 1


class TestBequeThreadSafety:
    """Test concurrent access to Beque."""

    async def test_concurrent_adds(self):
        """Test that concurrent adds are handled correctly."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, max_batch_size=100) as beque:

            async def add_items(start, count):
                for i in range(start, start + count):
                    await beque.add(f"item{i}")

            # Add items concurrently
            await asyncio.gather(add_items(0, 10), add_items(10, 10), add_items(20, 10))

            stats = beque.stats
            assert stats["queued"] == 30

    async def test_concurrent_add_and_flush(self):
        """Test concurrent adding and manual flushing."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, max_batch_size=100) as beque:

            async def add_continuously():
                for i in range(20):
                    await beque.add(f"item{i}")
                    await asyncio.sleep(0.01)

            async def flush_periodically():
                for _ in range(5):
                    await asyncio.sleep(0.05)
                    await beque.flush(force=True)

            await asyncio.gather(add_continuously(), flush_periodically())

            # All items should eventually be processed
            final_stats = beque.stats
            assert final_stats["items"] == 20

    async def test_concurrent_add_many_operations(self):
        """Test concurrent add_many operations with overlapping batches."""
        all_processed = []
        processing_lock = asyncio.Lock()

        async def thread_safe_handler(batch):
            async with processing_lock:
                all_processed.extend(batch)
                await asyncio.sleep(0.001)  # Small delay to increase contention

        async with Beque(on_flush=thread_safe_handler, max_batch_size=5) as beque:

            async def add_batch(batch_id, size):
                items = [f"batch{batch_id}_item{i}" for i in range(size)]
                await beque.add_many(items)

            # Create multiple concurrent batches
            await asyncio.gather(*[add_batch(i, 8) for i in range(10)])

            # Wait for all processing to complete
            await asyncio.sleep(0.5)

        # Should process all 80 items (10 batches x 8 items each)
        assert len(all_processed) == 80

        # Verify all items are unique (no duplicates from race conditions)
        assert len(set(all_processed)) == 80

    async def test_high_concurrency_stress_test(self):
        """Stress test with many concurrent producers and consumers."""
        processed_items = []
        processing_lock = asyncio.Lock()

        async def collecting_handler(batch):
            async with processing_lock:
                processed_items.extend(batch)

        async with Beque(
            on_flush=collecting_handler, max_batch_size=20, flush_interval=0.05
        ) as beque:

            async def producer(producer_id, item_count):
                for i in range(item_count):
                    await beque.add(f"p{producer_id}_i{i}")
                    # Occasional small delays to create realistic timing
                    if i % 10 == 0:
                        await asyncio.sleep(0.001)

            # Run many concurrent producers
            num_producers = 50
            items_per_producer = 20

            await asyncio.gather(
                *[producer(pid, items_per_producer) for pid in range(num_producers)]
            )

            # Wait for all processing
            await asyncio.sleep(1.0)

        expected_total = num_producers * items_per_producer
        assert len(processed_items) == expected_total

        # Verify no item corruption (all items should be valid format)
        for item in processed_items:
            assert item.startswith("p")
            assert "_i" in item


class TestBequeRealWorldScenarios:
    """Test real-world usage scenarios."""

    async def test_database_batch_insert_simulation(self):
        """Simulate database batch inserts with realistic timing."""
        inserted_records = []
        insert_times = []

        async def db_insert_handler(batch):
            # Simulate database insert time proportional to batch size
            insert_time = len(batch) * 0.002  # 2ms per record
            await asyncio.sleep(insert_time)

            inserted_records.extend(batch)
            insert_times.append(time.monotonic())

        # Configure for database-like batching
        async with Beque(
            on_flush=db_insert_handler,
            max_batch_size=50,  # Reasonable DB batch size
            flush_interval=0.5,  # Half second timeout
        ) as beque:
            # Simulate incoming user data at varying rates
            for hour in range(3):  # Simulate 3 hours of data
                # Peak hours have more data
                items_this_hour = 200 if hour == 1 else 100

                for i in range(items_this_hour):
                    user_record = {
                        "hour": hour,
                        "user_id": i,
                        "timestamp": time.time(),
                        "data": f"user_data_{hour}_{i}",
                    }
                    await beque.add(user_record)

                    # Vary the input rate
                    if hour == 1:  # Peak hour - faster input
                        await asyncio.sleep(0.001)
                    else:
                        await asyncio.sleep(0.005)

        total_expected = 100 + 200 + 100  # 400 records
        assert len(inserted_records) == total_expected

        # Verify batching efficiency
        assert len(insert_times) <= 10  # Should be much fewer inserts than records

    async def test_log_aggregation_scenario(self):
        """Simulate log aggregation with bursty traffic."""
        aggregated_logs = []

        async def log_aggregator(batch):
            # Simulate log processing
            await asyncio.sleep(0.01)

            # Group logs by level
            log_summary = {
                "batch_size": len(batch),
                "timestamp": time.monotonic(),
                "errors": len([log for log in batch if log.get("level") == "ERROR"]),
                "warnings": len([log for log in batch if log.get("level") == "WARN"]),
                "infos": len([log for log in batch if log.get("level") == "INFO"]),
            }
            aggregated_logs.append(log_summary)

        async with Beque(
            on_flush=log_aggregator,
            max_batch_size=25,
            flush_interval=0.2,
        ) as beque:
            # Simulate different types of log events
            log_levels = ["INFO", "WARN", "ERROR"]

            # Normal operation
            for i in range(50):
                log_entry = {
                    "level": random.choice(log_levels),
                    "message": f"Log message {i}",
                    "timestamp": time.time(),
                }
                await beque.add(log_entry)
                await asyncio.sleep(0.01)

            # Simulate error burst
            for i in range(20):
                error_log = {
                    "level": "ERROR",
                    "message": f"Burst error {i}",
                    "timestamp": time.time(),
                }
                await beque.add(error_log)
                # No delay - simulate burst

        assert len(aggregated_logs) >= 2  # Should have multiple batches

        # Verify total logs processed
        total_processed = sum(batch["batch_size"] for batch in aggregated_logs)
        assert total_processed == 70  # 50 normal + 20 error burst

    async def test_api_rate_limiting_scenario(self):
        """Simulate API calls with rate limiting."""
        api_calls = []
        last_call_time = 0

        async def rate_limited_api_handler(batch):
            nonlocal last_call_time
            current_time = time.monotonic()

            # Simulate API rate limiting (min 100ms between calls)
            if last_call_time > 0:
                time_since_last = current_time - last_call_time
                if time_since_last < 0.1:
                    await asyncio.sleep(0.1 - time_since_last)

            # Process the API calls
            for item in batch:
                api_calls.append(
                    {
                        "data": item,
                        "processed_at": time.monotonic(),
                    }
                )

            last_call_time = time.monotonic()

        async with Beque(
            on_flush=rate_limited_api_handler,
            max_batch_size=5,  # Small batches for API
            flush_interval=0.15,  # Slightly longer than rate limit
        ) as beque:
            # Add API requests rapidly
            for i in range(30):
                api_request = f"api_call_{i}"
                await beque.add(api_request)
                await asyncio.sleep(0.01)  # Much faster than rate limit

        assert len(api_calls) == 30

        # Verify rate limiting worked (batches should be spaced out)
        if len(api_calls) >= 10:  # Only check if we have enough calls
            # Check that we didn't process everything instantly
            total_time = api_calls[-1]["processed_at"] - api_calls[0]["processed_at"]
            min_expected_time = (
                len(api_calls) / 5
            ) * 0.1  # 5 items per batch, 0.1s between batches
            assert (
                total_time >= min_expected_time * 0.5
            )  # Allow 50% tolerance for timing variations

    async def test_event_streaming_with_backpressure(self):
        """Test handling of backpressure in event streaming."""
        processed_events = []
        processing_slow = False

        async def event_processor(batch):
            # Simulate variable processing speed
            processing_time = 0.1 if processing_slow else 0.01
            await asyncio.sleep(processing_time)

            processed_events.extend(batch)

        async with Beque(
            on_flush=event_processor,
            max_batch_size=10,
            flush_interval=0.05,
        ) as beque:
            # Start with fast processing
            for i in range(20):
                await beque.add(f"event_{i}")
                await asyncio.sleep(0.002)

            # Switch to slow processing to create backpressure
            processing_slow = True

            for i in range(20, 40):
                await beque.add(f"event_{i}")
                await asyncio.sleep(0.002)

            # Back to fast processing
            processing_slow = False

            for i in range(40, 60):
                await beque.add(f"event_{i}")
                await asyncio.sleep(0.002)

        assert len(processed_events) == 60

        # Events should maintain order despite backpressure
        for i, event in enumerate(processed_events):
            assert event == f"event_{i}"

    async def test_metrics_collection_scenario(self):
        """Test metrics collection with periodic aggregation."""
        collected_metrics = []

        async def metrics_aggregator(batch):
            # Simulate metrics aggregation
            await asyncio.sleep(0.005)

            # Aggregate numeric metrics
            metric_sum = sum(item.get("value", 0) for item in batch)
            metric_count = len(batch)

            aggregated = {
                "sum": metric_sum,
                "count": metric_count,
                "avg": metric_sum / metric_count if metric_count > 0 else 0,
                "timestamp": time.monotonic(),
            }
            collected_metrics.append(aggregated)

        async with Beque(
            on_flush=metrics_aggregator,
            max_batch_size=15,
            flush_interval=0.1,  # Aggregate every 100ms
        ) as beque:
            # Simulate steady stream of metrics
            for _i in range(100):
                metric = {
                    "metric_name": "response_time",
                    "value": random.uniform(10, 200),  # 10-200ms response times
                    "timestamp": time.time(),
                }
                await beque.add(metric)
                await asyncio.sleep(0.01)

        assert len(collected_metrics) >= 5  # Should have multiple aggregation windows

        # Verify all metrics were processed
        total_metrics = sum(batch["count"] for batch in collected_metrics)
        assert total_metrics == 100

        # Verify averages are reasonable
        for batch in collected_metrics:
            assert 10 <= batch["avg"] <= 200

    async def test_cleanup_with_pending_work(self):
        """Test cleanup behavior when work is still pending."""
        cleanup_handler_calls = []

        async def cleanup_aware_handler(batch):
            cleanup_handler_calls.append(
                {
                    "batch_size": len(batch),
                    "items": batch.copy(),
                    "timestamp": time.monotonic(),
                }
            )
            await asyncio.sleep(0.05)  # Simulate some processing time

        beque = Beque(
            on_flush=cleanup_aware_handler,
            max_batch_size=20,
            flush_interval=1.0,  # Long interval to ensure cleanup flush
        )

        await beque.start()

        # Add items that won't trigger size-based flush
        for i in range(15):
            await beque.add(f"cleanup_item_{i}")

        # Items should be queued but not yet flushed
        stats = beque.stats
        assert stats["queued"] == 15
        assert stats["flushes"] == 0

        # Stop should flush remaining items
        await beque.stop()

        assert len(cleanup_handler_calls) == 1
        assert cleanup_handler_calls[0]["batch_size"] == 15

        # Verify all items were flushed
        final_stats = beque.stats
        assert final_stats["queued"] == 0
        assert final_stats["items"] == 15
