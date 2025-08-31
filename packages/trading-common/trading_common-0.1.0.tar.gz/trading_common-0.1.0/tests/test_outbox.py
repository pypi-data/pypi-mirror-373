from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from trading_common.db import DB
from trading_common.outbox import OutboxProcessor


@pytest_asyncio.fixture
async def mock_db() -> DB:
    """Mock database fixture for testing"""
    db = DB("mock://test")

    # Mock the pool
    mock_pool = MagicMock()
    mock_pool.is_closed.return_value = False
    db.pool = mock_pool

    # Mock connection
    mock_connection = AsyncMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_connection

    return db


@pytest_asyncio.fixture
def outbox_processor(mock_db: DB) -> OutboxProcessor:
    """Outbox processor fixture"""
    return OutboxProcessor(mock_db)


@pytest.mark.asyncio
async def test_get_pending_events(
    mock_db: DB, outbox_processor: OutboxProcessor
) -> None:
    """Test getting pending events from outbox"""
    # Ensure pool is not None for type safety
    assert mock_db.pool is not None
    mock_connection = mock_db.pool.acquire.return_value.__aenter__.return_value

    # Mock fetch results
    mock_rows = [
        MagicMock(
            __getitem__=lambda self, key: {
                "event_id": "uuid-1",
                "topic": "topic1",
                "key": "key1",
                "payload": {"data": "value1"},
            }[key]
        ),
        MagicMock(
            __getitem__=lambda self, key: {
                "event_id": "uuid-2",
                "topic": "topic2",
                "key": "key2",
                "payload": {"data": "value2"},
            }[key]
        ),
    ]
    mock_connection.fetch.return_value = mock_rows

    # Get pending events
    events = await outbox_processor.get_pending_events(mock_connection, limit=10)

    assert len(events) == 2
    assert events[0][1] == "topic1"  # topic
    assert events[0][2] == "key1"  # key
    assert events[0][3] == {"data": "value1"}  # payload


@pytest.mark.asyncio
async def test_mark_published(mock_db: DB, outbox_processor: OutboxProcessor) -> None:
    """Test marking events as published"""
    # Ensure pool is not None for type safety
    assert mock_db.pool is not None
    mock_connection = mock_db.pool.acquire.return_value.__aenter__.return_value

    event_id = "uuid-1"

    # Mark as published
    await outbox_processor.mark_published(mock_connection, event_id)

    mock_connection.execute.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup_old_events(
    mock_db: DB, outbox_processor: OutboxProcessor
) -> None:
    """Test cleanup of old published events"""
    # Ensure pool is not None for type safety
    assert mock_db.pool is not None
    mock_connection = mock_db.pool.acquire.return_value.__aenter__.return_value

    # Cleanup old events
    await outbox_processor.cleanup_old_events(mock_connection, days_old=7)

    mock_connection.execute.assert_called_once()
