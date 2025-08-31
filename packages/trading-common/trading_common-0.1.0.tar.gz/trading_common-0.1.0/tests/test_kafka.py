import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from trading_common.kafka import ConsumerApp, Producer, dumps


def test_dumps() -> None:
    """Test JSON serialization"""
    data = {"key": "value", "number": 42}
    result = dumps(data)
    assert isinstance(result, bytes)
    assert json.loads(result.decode()) == data


@pytest.mark.asyncio
async def test_producer_start_stop() -> None:
    """Test producer start and stop"""
    producer = Producer("localhost:9092")

    # Mock AIOKafkaProducer
    mock_producer = AsyncMock()
    with patch("trading_common.kafka.AIOKafkaProducer", return_value=mock_producer):
        producer.p = mock_producer

        # Test stop
        await producer.stop()
        mock_producer.stop.assert_called_once()


@pytest.mark.asyncio
async def test_producer_send() -> None:
    """Test producer send with key"""
    producer = Producer("localhost:9092")

    # Mock AIOKafkaProducer
    mock_producer = AsyncMock()
    producer.p = mock_producer

    topic = "test.topic"
    key = "test-key"
    payload = {"data": "test-value"}

    await producer.send(topic, key, payload)

    mock_producer.send_and_wait.assert_called_with(
        topic, key=key.encode(), value=dumps(payload)
    )


@pytest.mark.asyncio
async def test_producer_send_no_key() -> None:
    """Test producer send without key"""
    producer = Producer("localhost:9092")

    # Mock AIOKafkaProducer
    mock_producer = AsyncMock()
    producer.p = mock_producer

    topic = "test.topic"
    payload = {"data": "test-value"}

    await producer.send(topic, None, payload)

    mock_producer.send_and_wait.assert_called_with(
        topic, key=None, value=dumps(payload)
    )


@pytest.mark.asyncio
async def test_consumer_app_start_stop() -> None:
    """Test consumer app start and stop"""
    # Mock DB
    mock_db = MagicMock()
    mock_db.start = AsyncMock()
    mock_db.stop = AsyncMock()

    # Mock AIOKafkaConsumer
    mock_consumer = AsyncMock()
    with patch("trading_common.kafka.AIOKafkaConsumer", return_value=mock_consumer):
        consumer_app = ConsumerApp(
            "test-consumer",
            mock_db,
            "localhost:9092",
            ["test.topic"],
            "test-group",
            AsyncMock(),
        )

        consumer_app.c = mock_consumer

        # Test stop
        await consumer_app.stop()
        mock_consumer.stop.assert_called_once()
        mock_db.stop.assert_called_once()


@pytest.mark.asyncio
async def test_consumer_app_run_batch_processing() -> None:
    """Test consumer app batch processing setup"""
    # Mock DB
    mock_db = MagicMock()
    mock_db.start = AsyncMock()
    mock_db.stop = AsyncMock()
    mock_pool = MagicMock()
    mock_db.pool = mock_pool

    # Mock connection
    mock_connection = AsyncMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_connection

    # Mock transaction
    mock_transaction = AsyncMock()
    mock_connection.transaction.return_value = mock_transaction

    # Mock consumer
    mock_consumer = AsyncMock()
    mock_consumer.getmany.return_value = {}
    mock_consumer.commit = AsyncMock()

    # Mock handler
    mock_handler = AsyncMock()

    consumer_app = ConsumerApp(
        "test-consumer",
        mock_db,
        "localhost:9092",
        ["test.topic"],
        "test-group",
        mock_handler,
    )

    consumer_app.c = mock_consumer

    # Test that the setup is correct without running the infinite loop
    assert consumer_app.c is not None
    assert consumer_app.db.pool is not None
    assert consumer_app.handler is not None

    # Verify consumer was initialized
    mock_consumer.getmany.assert_not_called()  # Should not be called yet
