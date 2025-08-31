from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from trading_common.db import DB


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

    # Mock transaction
    mock_transaction = AsyncMock()
    mock_connection.transaction.return_value = mock_transaction

    return db


@pytest.mark.asyncio
async def test_db_start_stop() -> None:
    """Test database start and stop"""
    db = DB("mock://test")

    # Test that pool starts as None
    assert db.pool is None

    # Test stop when pool is None (should not crash)
    await db.stop()

    # Test with mock pool
    mock_pool = AsyncMock()
    db.pool = mock_pool

    await db.stop()
    mock_pool.close.assert_called_once()


@pytest.mark.asyncio
async def test_idempotent_begin(mock_db: DB) -> None:
    """Test idempotent message processing"""
    # Ensure pool is not None for type safety
    assert mock_db.pool is not None
    mock_connection = mock_db.pool.acquire.return_value.__aenter__.return_value

    # Mock successful insert
    mock_connection.fetchval.return_value = 1

    result = await mock_db.idempotent_begin(mock_connection, "msg-1")
    assert result is True

    # Mock failed insert (already exists)
    mock_connection.fetchval.return_value = None

    result = await mock_db.idempotent_begin(mock_connection, "msg-1")
    assert result is False


@pytest.mark.asyncio
async def test_idempotent_finish(mock_db: DB) -> None:
    """Test marking message as finished"""
    # Ensure pool is not None for type safety
    assert mock_db.pool is not None
    mock_connection = mock_db.pool.acquire.return_value.__aenter__.return_value

    await mock_db.idempotent_finish(mock_connection, "msg-1")

    mock_connection.execute.assert_called_once()


@pytest.mark.asyncio
async def test_outbox_put(mock_db: DB) -> None:
    """Test putting message to outbox"""
    # Ensure pool is not None for type safety
    assert mock_db.pool is not None
    mock_connection = mock_db.pool.acquire.return_value.__aenter__.return_value

    topic = "test.topic"
    key = "test-key"
    payload = {"data": "test-value"}

    await mock_db.outbox_put(mock_connection, topic, key, payload)

    mock_connection.execute.assert_called_once()
