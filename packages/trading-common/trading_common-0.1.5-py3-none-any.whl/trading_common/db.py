import json
from typing import Any, Dict, Optional

import asyncpg

INIT_SQL = """
CREATE SCHEMA IF NOT EXISTS core;
CREATE TABLE IF NOT EXISTS core.inbox(
  message_id TEXT PRIMARY KEY,
  received_at timestamptz NOT NULL DEFAULT now(),
  processed_at timestamptz
);
CREATE TABLE IF NOT EXISTS core.outbox(
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic TEXT NOT NULL,
  key TEXT,
  payload JSONB NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  published_at timestamptz
);
CREATE INDEX IF NOT EXISTS ix_outbox_pub ON core.outbox(
    published_at NULLS FIRST, created_at
);
"""


class DB:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.pool: Optional[asyncpg.Pool] = None

    async def start(self) -> None:
        self.pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=5)
        async with self.pool.acquire() as con:
            await con.execute(INIT_SQL)

    async def stop(self) -> None:
        if self.pool:
            await self.pool.close()

    async def idempotent_begin(self, con: asyncpg.Connection, message_id: str) -> bool:
        sql = (
            "INSERT INTO core.inbox(message_id) VALUES($1) "
            "ON CONFLICT DO NOTHING RETURNING 1"
        )
        row = await con.fetchval(sql, message_id)
        return bool(row)

    async def idempotent_finish(self, con: asyncpg.Connection, message_id: str) -> None:
        await con.execute(
            "UPDATE core.inbox SET processed_at=now() WHERE message_id=$1",
            message_id,
        )

    async def outbox_put(
        self,
        con: asyncpg.Connection,
        topic: str,
        key: Optional[str],
        payload: Dict[str, Any],
    ) -> None:
        await con.execute(
            "INSERT INTO core.outbox(topic, key, payload) VALUES($1,$2,$3)",
            topic,
            key,
            json.dumps(payload),
        )
