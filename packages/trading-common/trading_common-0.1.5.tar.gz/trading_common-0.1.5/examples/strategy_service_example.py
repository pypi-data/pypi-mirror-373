"""
Example strategy service using trading-common components
"""
import asyncio
import json
from typing import Any, Dict, Optional

from trading_common.db import DB
from trading_common.kafka import ConsumerApp, Producer
from trading_common.outbox import OutboxProcessor
from trading_common.schema import ensure


async def handle_strategy_signal(
    con: Any, topic: str, key: Optional[str], payload: Dict[str, Any]
) -> None:
    """Handle incoming strategy signal"""
    print(f"Processing signal from {topic}: {payload}")

    # Validate payload against schema
    try:
        validated_payload = ensure("strategy.signal@v1", payload)
        print(f"Validated payload: {validated_payload}")
    except Exception as e:
        print(f"Schema validation failed: {e}")
        return

    # Process the signal (example: store in database)
    # In real implementation, you would:
    # 1. Analyze the signal
    # 2. Check risk limits
    # 3. Generate orders if conditions are met
    # 4. Store results in database

    # Example: Store signal in database
    await con.execute(
        "INSERT INTO strategy_signals (signal_id, data) VALUES ($1, $2)",
        payload.get("signal_id"),
        json.dumps(payload),
    )

    # Example: Put order request in outbox
    if payload.get("action") == "buy":
        order_request = {
            "order_id": f"order-{payload['signal_id']}",
            "symbol": payload.get("symbol"),
            "side": "buy",
            "quantity": payload.get("quantity"),
            "price": payload.get("price"),
        }
        await con.execute(
            "INSERT INTO core.outbox(topic, key, payload) VALUES($1,$2,$3)",
            "exec.order.request",
            order_request["order_id"],
            json.dumps(order_request),
        )


async def publish_market_data() -> None:
    """Example: Publish market data to Kafka"""
    producer = Producer("localhost:9092")
    await producer.start()

    try:
        # Example market data
        market_data = {
            "symbol": "BTCUSDT",
            "price": 50000.0,
            "timestamp": "2024-01-01T00:00:00Z",
        }

        await producer.send("md.price.update", "BTCUSDT", market_data)
        print("Published market data")
    finally:
        await producer.stop()


async def process_outbox_events() -> None:
    """Example: Process outbox events"""
    db = DB("postgresql://user:pass@localhost/trading")
    await db.start()

    try:
        outbox_processor = OutboxProcessor(db)
        # Ensure pool is not None for type safety
        if db.pool is None:
            raise RuntimeError("Database pool not initialized")

        async with db.pool.acquire() as con:
            # Get pending events
            events = await outbox_processor.get_pending_events(con, limit=10)
            print(f"Found {len(events)} pending events")

            # Process each event
            for event_id, topic, key, payload in events:
                print(f"Processing event {event_id} from {topic}")
                # In real implementation, you would publish to Kafka here
                # await kafka_producer.send(topic, key, payload)

                # Mark as published
                await outbox_processor.mark_published(con, event_id)

            # Cleanup old events
            await outbox_processor.cleanup_old_events(con, days_old=7)
    finally:
        await db.stop()


async def main() -> None:
    """Main function demonstrating the components"""
    print("Starting strategy service example...")

    # Initialize database
    db = DB("postgresql://user:pass@localhost/trading")
    await db.start()

    try:
        # Create consumer app
        consumer_app = ConsumerApp(
            name="strategy-service",
            db=db,
            bootstrap="localhost:9092",
            topics=["strategy.signals"],
            group_id="strategy-service-group",
            handler=handle_strategy_signal,
        )

        # Start consumer
        await consumer_app.start()
        print("Strategy service started")

        # Example: Publish some market data
        await publish_market_data()

        # Example: Process outbox events
        await process_outbox_events()

        # Keep running for a while to process messages
        print("Running for 10 seconds...")
        await asyncio.sleep(10)

    finally:
        await db.stop()
        print("Strategy service stopped")


if __name__ == "__main__":
    asyncio.run(main())
