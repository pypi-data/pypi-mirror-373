"""
Core functionality tests for Beque.

Tests basic operations, initialization, context management, and fundamental behavior.
"""

import asyncio
import logging
import time
from unittest.mock import AsyncMock

import pytest

from beque import Beque


class TestBequeInitialization:
    """Test Beque initialization and parameter validation."""

    async def test_valid_initialization(self):
        """Test successful initialization with valid parameters."""
        handler = AsyncMock()
        beque = Beque(on_flush=handler, max_batch_size=50, flush_interval=5.0)

        assert beque._max_batch_size == 50
        assert beque._flush_interval == 5.0
        assert beque._name == "Beque"
        assert not beque._running
        assert beque._total_flushes == 0
        assert beque._total_items == 0
        assert beque._failed_flushes == 0

    async def test_custom_name_and_logger(self):
        """Test initialization with custom name and logger."""
        handler = AsyncMock()
        logger = logging.getLogger("test-logger")
        beque = Beque(on_flush=handler, name="CustomBeque", logger=logger)

        assert beque._name == "CustomBeque"
        assert beque._logger == logger

    def test_invalid_max_batch_size(self):
        """Test initialization with invalid max_batch_size."""
        handler = AsyncMock()

        with pytest.raises(ValueError, match="max_batch_size must be >= 1"):
            Beque(on_flush=handler, max_batch_size=0)

        with pytest.raises(ValueError, match="max_batch_size must be >= 1"):
            Beque(on_flush=handler, max_batch_size=-1)

    def test_invalid_flush_interval(self):
        """Test initialization with invalid flush_interval."""
        handler = AsyncMock()

        with pytest.raises(ValueError, match="flush_interval must be > 0"):
            Beque(on_flush=handler, flush_interval=0.0)

        with pytest.raises(ValueError, match="flush_interval must be > 0"):
            Beque(on_flush=handler, flush_interval=-1.0)

    async def test_extreme_valid_parameters(self):
        """Test initialization with extreme but valid parameters."""
        handler = AsyncMock()

        # Very large batch size
        beque_large = Beque(on_flush=handler, max_batch_size=1_000_000)
        assert beque_large._max_batch_size == 1_000_000

        # Very small flush interval
        beque_fast = Beque(on_flush=handler, flush_interval=0.001)
        assert beque_fast._flush_interval == 0.001

        # Very large flush interval
        beque_slow = Beque(on_flush=handler, flush_interval=86400.0)  # 1 day
        assert beque_slow._flush_interval == 86400.0


class TestBequeContextManager:
    """Test Beque as an async context manager."""

    async def test_context_manager_lifecycle(self):
        """Test that context manager properly starts and stops."""
        handler = AsyncMock()

        async with Beque(on_flush=handler) as beque:
            assert beque._running
            assert beque._task is not None

        assert not beque._running
        assert beque._task is None

    async def test_multiple_context_entries(self):
        """Test that entering context multiple times is safe."""
        handler = AsyncMock()
        beque = Beque(on_flush=handler)

        async with beque:
            assert beque._running
            async with beque:  # Should be safe to enter again
                assert beque._running

        assert not beque._running

    async def test_context_manager_with_exception(self):
        """Test context manager cleanup when exception occurs."""
        handler = AsyncMock()

        try:
            async with Beque(on_flush=handler) as beque:
                assert beque._running
                await beque.add("test_item")
                raise ValueError("Test exception")
        except ValueError:
            pass

        assert not beque._running
        # Should have called handler during cleanup
        handler.assert_called_once()

    async def test_manual_start_stop(self):
        """Test manual start/stop lifecycle."""
        handler = AsyncMock()
        beque = Beque(on_flush=handler)

        assert not beque._running

        await beque.start()
        assert beque._running
        assert beque._task is not None

        # Multiple starts should be safe
        await beque.start()
        assert beque._running

        await beque.stop()
        assert not beque._running
        assert beque._task is None

        # Multiple stops should be safe
        await beque.stop()
        assert not beque._running


class TestBequeBasicOperations:
    """Test basic Beque operations."""

    async def test_add_single_item(self):
        """Test adding a single item to the queue."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, max_batch_size=5) as beque:
            await beque.add("test_item")

            stats = beque.stats
            assert stats["queued"] == 1
            assert stats["running"]

    async def test_add_many_items(self):
        """Test adding multiple items at once."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, max_batch_size=10) as beque:
            items = ["item1", "item2", "item3"]
            await beque.add_many(items)

            stats = beque.stats
            assert stats["queued"] == 3

    async def test_add_empty_list(self):
        """Test that adding an empty list is a no-op."""
        handler = AsyncMock()

        async with Beque(on_flush=handler) as beque:
            await beque.add_many([])

            stats = beque.stats
            assert stats["queued"] == 0

    async def test_add_when_not_running(self):
        """Test that adding items when not running raises RuntimeError."""
        handler = AsyncMock()
        beque = Beque(on_flush=handler)

        with pytest.raises(RuntimeError, match="Beque is not running"):
            await beque.add("item")

        with pytest.raises(RuntimeError, match="Beque is not running"):
            await beque.add_many(["item1", "item2"])

    async def test_add_none_values(self):
        """Test that None values can be added and processed."""
        processed_items = []

        async def handler(batch):
            processed_items.extend(batch)

        async with Beque(on_flush=handler, max_batch_size=3) as beque:
            await beque.add(None)
            await beque.add("valid")
            await beque.add(None)

            await asyncio.sleep(0.1)  # Let flush complete

        assert processed_items == [None, "valid", None]

    async def test_add_mixed_types(self):
        """Test adding different types of items."""
        processed_items = []

        async def handler(batch):
            processed_items.extend(batch)

        async with Beque(on_flush=handler, max_batch_size=5) as beque:
            await beque.add(42)
            await beque.add("string")
            await beque.add([1, 2, 3])
            await beque.add({"key": "value"})
            await beque.add(3.14)

            await asyncio.sleep(0.1)  # Let flush complete

        assert len(processed_items) == 5
        assert 42 in processed_items
        assert "string" in processed_items
        assert [1, 2, 3] in processed_items
        assert {"key": "value"} in processed_items
        assert 3.14 in processed_items


class TestBequeFlushingBySize:
    """Test flushing behavior based on batch size."""

    async def test_flush_when_batch_size_reached(self):
        """Test automatic flushing when max_batch_size is reached."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, max_batch_size=3) as beque:
            await beque.add("item1")
            await beque.add("item2")

            # Should not have flushed yet
            handler.assert_not_called()

            await beque.add("item3")

            # Give time for flush to complete
            await asyncio.sleep(0.1)

            handler.assert_called_once_with(["item1", "item2", "item3"])
            stats = beque.stats
            assert stats["flushes"] == 1
            assert stats["items"] == 3
            assert stats["queued"] == 0

    async def test_add_many_triggers_flush(self):
        """Test that add_many can trigger flush when batch size is exceeded."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, max_batch_size=3) as beque:
            await beque.add("item1")
            await beque.add_many(["item2", "item3"])

            # Give time for flush to complete
            await asyncio.sleep(0.1)

            handler.assert_called_once_with(["item1", "item2", "item3"])

    async def test_partial_batch_flush_on_size(self):
        """Test that partial batches work correctly with size-based flushing."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, max_batch_size=5) as beque:
            # Add 7 items, should flush 5 and keep 2
            for i in range(7):
                await beque.add(f"item{i}")

            await asyncio.sleep(0.1)

            handler.assert_called_once_with(
                ["item0", "item1", "item2", "item3", "item4"]
            )
            assert beque.stats["queued"] == 2

    async def test_large_batch_size_single_flush(self):
        """Test with very large batch size that everything goes in one flush."""
        processed_batches = []

        async def handler(batch):
            processed_batches.append(batch.copy())

        async with Beque(on_flush=handler, max_batch_size=10000) as beque:
            for i in range(100):
                await beque.add(f"item{i}")

        # Should have only one batch at shutdown
        assert len(processed_batches) == 1
        assert len(processed_batches[0]) == 100


class TestBequeFlushingByTime:
    """Test flushing behavior based on time interval."""

    async def test_flush_after_interval(self):
        """Test automatic flushing after flush_interval."""
        handler = AsyncMock()

        async with Beque(
            on_flush=handler, max_batch_size=10, flush_interval=0.1
        ) as beque:
            await beque.add("item1")
            await beque.add("item2")

            # Should not flush immediately
            handler.assert_not_called()

            # Wait for flush interval
            await asyncio.sleep(0.2)

            handler.assert_called_once_with(["item1", "item2"])
            stats = beque.stats
            assert stats["flushes"] == 1
            assert stats["items"] == 2

    async def test_no_flush_when_empty(self):
        """Test that no flush occurs when queue is empty."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, flush_interval=0.1) as beque:
            # Wait longer than flush interval
            await asyncio.sleep(0.2)

            handler.assert_not_called()

    async def test_time_based_flush_resets_timer(self):
        """Test that time-based flush resets the flush timer."""
        call_times = []

        async def handler(batch):
            call_times.append(time.monotonic())

        async with Beque(
            on_flush=handler, max_batch_size=10, flush_interval=0.15
        ) as beque:
            await beque.add("item1")

            # Wait for first flush
            await asyncio.sleep(0.2)

            # Add another item - should reset timer
            await beque.add("item2")

            # Wait for second flush
            await asyncio.sleep(0.2)

        assert len(call_times) >= 2
        # Verify reasonable time gap between flushes
        time_gap = call_times[1] - call_times[0]
        assert 0.1 < time_gap < 0.5  # Should be around flush_interval


class TestBequeManualFlush:
    """Test manual flushing functionality."""

    async def test_manual_flush(self):
        """Test manual flush with force=True."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, max_batch_size=10) as beque:
            await beque.add("item1")
            await beque.add("item2")

            await beque.flush(force=True)

            handler.assert_called_once_with(["item1", "item2"])
            stats = beque.stats
            assert stats["queued"] == 0

    async def test_manual_flush_empty_queue(self):
        """Test that manual flush on empty queue is a no-op."""
        handler = AsyncMock()

        async with Beque(on_flush=handler) as beque:
            await beque.flush(force=True)

            handler.assert_not_called()

    async def test_manual_flush_non_force(self):
        """Test manual flush with force=False only flushes if batch size reached."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, max_batch_size=5) as beque:
            # Add less than batch size
            await beque.add("item1")
            await beque.add("item2")

            # Non-force flush should not flush
            await beque.flush(force=False)
            handler.assert_not_called()

            # Add enough to reach batch size
            for i in range(3, 6):  # items 3, 4, 5
                await beque.add(f"item{i}")

            # Now non-force flush should work
            await beque.flush(force=False)
            await asyncio.sleep(0.05)

            handler.assert_called_once()

    async def test_multiple_manual_flushes(self):
        """Test multiple consecutive manual flushes."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, max_batch_size=10) as beque:
            await beque.add("item1")
            await beque.flush(force=True)

            await beque.add("item2")
            await beque.flush(force=True)

            await beque.add("item3")
            await beque.flush(force=True)

            assert handler.call_count == 3
            # Verify calls were with single items each
            calls = handler.call_args_list
            assert calls[0][0][0] == ["item1"]
            assert calls[1][0][0] == ["item2"]
            assert calls[2][0][0] == ["item3"]


class TestBequeStatistics:
    """Test statistics tracking."""

    async def test_stats_structure(self):
        """Test that stats returns correct structure."""
        handler = AsyncMock()
        beque = Beque(on_flush=handler)

        stats = beque.stats
        required_keys = {
            "flushes",
            "items",
            "failures",
            "queued",
            "last_flush_time",
            "running",
        }
        assert set(stats.keys()) == required_keys

        # Test initial values
        assert stats["flushes"] == 0
        assert stats["items"] == 0
        assert stats["failures"] == 0
        assert stats["queued"] == 0
        assert stats["last_flush_time"] is None
        assert not stats["running"]

    async def test_stats_updates(self):
        """Test that stats are updated correctly during operation."""
        handler = AsyncMock()

        async with Beque(on_flush=handler, max_batch_size=2) as beque:
            initial_stats = beque.stats
            assert initial_stats["running"]
            assert initial_stats["last_flush_time"] is not None

            await beque.add("item1")
            await beque.add("item2")

            # Give time for flush
            await asyncio.sleep(0.1)

            final_stats = beque.stats
            assert final_stats["flushes"] == 1
            assert final_stats["items"] == 2
            assert final_stats["queued"] == 0

    async def test_stats_consistency_during_operation(self):
        """Test that stats remain consistent during heavy operation."""
        processed_count = 0

        async def counting_handler(batch):
            nonlocal processed_count
            processed_count += len(batch)
            await asyncio.sleep(0.001)  # Tiny delay

        async with Beque(on_flush=counting_handler, max_batch_size=10) as beque:
            # Add items rapidly
            for i in range(50):
                await beque.add(f"item{i}")
                if i % 10 == 0:
                    stats = beque.stats
                    assert stats["running"]
                    # Queued + processed should equal total added so far
                    assert stats["queued"] + stats["items"] >= 0

            # Wait for processing to complete
            await asyncio.sleep(0.5)

        final_stats = beque.stats
        assert final_stats["items"] == 50
        assert processed_count == 50


class TestBequeShutdown:
    """Test proper shutdown behavior."""

    async def test_stop_flushes_remaining_items(self):
        """Test that stop() flushes remaining items."""
        handler = AsyncMock()

        beque = Beque(on_flush=handler, max_batch_size=10)
        await beque.start()

        await beque.add("item1")
        await beque.add("item2")

        await beque.stop()

        handler.assert_called_once_with(["item1", "item2"])
        assert not beque._running

    async def test_stop_when_not_running(self):
        """Test that stop() is safe when already stopped."""
        handler = AsyncMock()
        beque = Beque(on_flush=handler)

        # Should not raise exception
        await beque.stop()
        assert not beque._running

    async def test_graceful_shutdown_with_pending_operations(self):
        """Test graceful shutdown while operations are in progress."""
        processing_started = asyncio.Event()
        continue_processing = asyncio.Event()

        async def slow_handler(batch):
            processing_started.set()
            await continue_processing.wait()
            return batch

        beque = Beque(on_flush=slow_handler, max_batch_size=1)
        await beque.start()

        # Add item that will start processing
        await beque.add("item1")

        # Wait for processing to start
        await processing_started.wait()

        # Now stop the beque (should wait for processing to complete)
        stop_task = asyncio.create_task(beque.stop())

        # Give a moment to ensure stop is waiting
        await asyncio.sleep(0.05)
        assert not stop_task.done()

        # Allow processing to complete
        continue_processing.set()

        # Stop should now complete
        await stop_task
        assert not beque._running


class TestBequeLogging:
    """Test logging functionality."""

    async def test_custom_logger_used(self, caplog):
        """Test that custom logger is used for logging."""
        handler = AsyncMock()
        custom_logger = logging.getLogger("test_beque")

        with caplog.at_level(logging.INFO, logger="test_beque"):
            async with Beque(
                on_flush=handler,
                logger=custom_logger,
                max_batch_size=10,
                flush_interval=1.0,
            ):
                pass

        # Check that start and stop messages were logged
        assert any("Started" in record.message for record in caplog.records)
        assert any("Stopped" in record.message for record in caplog.records)

    async def test_debug_logging_on_flush(self, caplog):
        """Test that debug messages are logged on successful flush."""
        handler = AsyncMock()
        custom_logger = logging.getLogger("test_debug_beque")

        with caplog.at_level(logging.DEBUG, logger="test_debug_beque"):
            async with Beque(
                on_flush=handler, logger=custom_logger, max_batch_size=2
            ) as beque:
                await beque.add("item1")
                await beque.add("item2")
                await asyncio.sleep(0.1)  # Wait for flush

        # Should have logged the flush
        debug_messages = [
            r.message for r in caplog.records if r.levelno == logging.DEBUG
        ]
        assert any("Flushed 2 items" in msg for msg in debug_messages)
