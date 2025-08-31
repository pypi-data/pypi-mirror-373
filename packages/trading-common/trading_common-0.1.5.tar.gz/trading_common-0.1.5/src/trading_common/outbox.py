from typing import Any, Dict, List, Optional, Tuple

import asyncpg


class OutboxProcessor:
    def __init__(self, db: Any) -> None:
        self.db = db

    async def get_pending_events(
        self, con: asyncpg.Connection, limit: int = 100
    ) -> List[Tuple[str, str, Optional[str], Dict[str, Any]]]:
        """Get pending events from outbox ordered by creation time"""
        rows = await con.fetch(
            """SELECT event_id::text, topic, key, payload
               FROM core.outbox
               WHERE published_at IS NULL
               ORDER BY created_at
               LIMIT $1""",
            limit,
        )
        return [
            (str(row["event_id"]), row["topic"], row["key"], row["payload"])
            for row in rows
        ]

    async def mark_published(self, con: asyncpg.Connection, event_id: str) -> None:
        """Mark event as published"""
        await con.execute(
            "UPDATE core.outbox SET published_at = now() WHERE event_id = $1::uuid",
            event_id,
        )

    async def cleanup_old_events(
        self, con: asyncpg.Connection, days_old: int = 7
    ) -> None:
        """Clean up old published events"""
        await con.execute(
            """DELETE FROM core.outbox
               WHERE published_at IS NOT NULL
               AND published_at < now() - interval '$1 days'""",
            days_old,
        )
