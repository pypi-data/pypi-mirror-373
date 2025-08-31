import json
from typing import Any, Awaitable, Callable, Dict, Optional

import asyncpg
import ujson
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


def dumps(obj: Dict[str, Any]) -> bytes:
    result: str = ujson.dumps(obj, ensure_ascii=False)
    return result.encode()


class Producer:
    def __init__(self, bootstrap: str) -> None:
        self.bootstrap = bootstrap
        self.p: Optional[AIOKafkaProducer] = None

    async def start(self) -> None:
        self.p = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap, acks="all", linger_ms=10
        )
        await self.p.start()

    async def stop(self) -> None:
        if self.p:
            await self.p.stop()

    async def send(
        self, topic: str, key: Optional[str], payload: Dict[str, Any]
    ) -> None:
        assert self.p
        k = key.encode() if key is not None else None
        await self.p.send_and_wait(topic, key=k, value=dumps(payload))


class ConsumerApp:
    def __init__(
        self,
        name: str,
        db: Any,
        bootstrap: str,
        topics: list[str],
        group_id: str,
        handler: Callable[
            [asyncpg.Connection, str, Optional[str], Dict[str, Any]], Awaitable[None]
        ],
    ) -> None:
        self.name = name
        self.db = db
        self.bootstrap = bootstrap
        self.topics = topics
        self.group_id = group_id
        self.handler = handler
        self.c: Optional[AIOKafkaConsumer] = None

    async def start(self) -> None:
        await self.db.start()
        self.c = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap,
            group_id=self.group_id,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            max_poll_records=256,
        )
        await self.c.start()

    async def stop(self) -> None:
        if self.c:
            await self.c.stop()
        await self.db.stop()

    async def run(self) -> None:
        assert self.c and self.db.pool
        while True:
            batch = await self.c.getmany(timeout_ms=1000, max_records=512)
            for tp, msgs in batch.items():
                async with self.db.pool.acquire() as con:
                    tx = con.transaction()
                    await tx.start()
                    try:
                        for m in msgs:
                            payload = json.loads(m.value.decode())
                            msg_id = (
                                payload.get("event_id")
                                or f"{tp.topic}:{m.partition}:{m.offset}"
                            )
                            if not await self.db.idempotent_begin(con, msg_id):
                                continue
                            key = m.key.decode() if m.key else None
                            await self.handler(con, tp.topic, key, payload)
                            await self.db.idempotent_finish(con, msg_id)
                        await tx.commit()
                    except Exception:
                        await tx.rollback()
                        raise
            await self.c.commit()
