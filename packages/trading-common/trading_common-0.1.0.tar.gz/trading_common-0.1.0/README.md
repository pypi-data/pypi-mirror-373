# Trading Common

Common utilities for trading platform including Kafka producer/consumer wrappers, Postgres inbox/outbox patterns, and event validation through trading-contracts.

## Features

- **Database**: AsyncPG wrapper with inbox/outbox tables and idempotency support
- **Kafka**: AIOKafka producer/consumer wrappers with transaction handling
- **Schema Validation**: Event validation using trading-contracts schemas
- **Outbox Pattern**: Reliable message publishing with database persistence

## Installation

```bash
# Install in development mode
pip install -e ".[dev]"

# Install production dependencies only
pip install -e .
```

## Quick Start

### Database Setup

```python
from trading_common.db import DB

db = DB("postgresql://user:pass@localhost:5432/dbname")
await db.start()

# Use in transactions
async with db.pool.acquire() as con:
    tx = con.transaction()
    await tx.start()
    try:
        # Your business logic here
        await db.outbox_put(con, "topic", "key", {"data": "value"})
        await tx.commit()
    except Exception:
        await tx.rollback()
        raise

await db.stop()
```

### Kafka Consumer

```python
from trading_common.kafka import ConsumerApp
from trading_common.schema import ensure

async def handler(con, topic, key, payload):
    # Validate event schema
    ensure("md.candle.closed@v1", payload)

    # Process the event
    # ... your business logic ...

    # Optionally publish to outbox
    await db.outbox_put(con, "strategy.signal@v1", key, {"signal": "buy"})

# Create and run consumer
consumer = ConsumerApp(
    name="strategy-service",
    db=db,
    bootstrap="localhost:9092",
    topics=["market-data"],
    group_id="strategy-group",
    handler=handler
)

await consumer.start()
await consumer.run()  # Runs indefinitely
```

### Kafka Producer

```python
from trading_common.kafka import Producer

producer = Producer("localhost:9092")
await producer.start()

# Send messages
await producer.send("topic", "key", {"data": "value"})

await producer.stop()
```

### Outbox Processing

```python
from trading_common.outbox import OutboxProcessor

outbox = OutboxProcessor(db)

async with db.pool.acquire() as con:
    # Get pending events
    events = await outbox.get_pending_events(con, limit=100)

    for event_id, topic, key, payload in events:
        # Publish to Kafka
        await producer.send(topic, key, payload)

        # Mark as published
        await outbox.mark_published(con, event_id)

    # Clean up old events
    await outbox.cleanup_old_events(con, days_old=7)
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
isort src tests

# Type checking
mypy src

# Run with coverage
pytest --cov=trading_common --cov-report=term-missing
```

## Architecture

- **Inbox Pattern**: Ensures idempotent message processing
- **Outbox Pattern**: Reliable message publishing with database persistence
- **Transaction Safety**: All operations wrapped in database transactions
- **Schema Validation**: Events validated against JSON schemas before processing

## Dependencies

- Python 3.10+
- asyncpg: Async PostgreSQL driver
- aiokafka: Async Kafka client
- ujson: Fast JSON serializer
- trading-contracts: Schema validation
- jsonschema: JSON schema validation
