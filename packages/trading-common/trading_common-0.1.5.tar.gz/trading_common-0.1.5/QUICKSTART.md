# Quick Start Guide

## Installation

```bash
cd trading-common-py
pip install -e ".[dev]"
```

## Basic Usage

### 1. Database Connection

```python
from trading_common.db import DB

db = DB("postgresql://user:pass@localhost:5432/dbname")
await db.start()

# Use in transactions
async with db.pool.acquire() as con:
    tx = con.transaction()
    await tx.start()
    try:
        await db.outbox_put(con, "topic", "key", {"data": "value"})
        await tx.commit()
    except Exception:
        await tx.rollback()
        raise

await db.stop()
```

### 2. Kafka Consumer

```python
from trading_common.kafka import ConsumerApp
from trading_common.schema import ensure

async def handler(con, topic, key, payload):
    ensure("md.candle.closed@v1", payload)  # Validate schema
    # Your business logic here
    await db.outbox_put(con, "strategy.signal@v1", key, {"signal": "buy"})

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

### 3. Kafka Producer

```python
from trading_common.kafka import Producer

producer = Producer("localhost:9092")
await producer.start()

await producer.send("topic", "key", {"data": "value"})
await producer.stop()
```

### 4. Outbox Processing

```python
from trading_common.outbox import OutboxProcessor

outbox = OutboxProcessor(db)

async with db.pool.acquire() as con:
    events = await outbox.get_pending_events(con, limit=100)

    for event_id, topic, key, payload in events:
        await producer.send(topic, key, payload)
        await outbox.mark_published(con, event_id)
```

## Testing

```bash
pytest                    # Run all tests
pytest -m unit          # Run only unit tests
pytest -v               # Verbose output
```

## Code Quality

```bash
black src tests         # Format code
isort src tests         # Sort imports
mypy src               # Type checking
```
