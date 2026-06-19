from dataclasses import dataclass

from models.database import get_connection


@dataclass(slots=True)
class AdminStats:
    total_bookings: int
    popular_service: str | None
    unique_clients: int


class StatsService:
    async def get_monthly_stats(self) -> AdminStats:
        db = await get_connection()

        cursor = await db.execute(
            """
            SELECT COUNT(*) AS cnt FROM bookings
            WHERE status = 'active'
              AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now', 'localtime')
            """
        )
        total = (await cursor.fetchone())["cnt"]

        cursor = await db.execute(
            """
            SELECT s.name, COUNT(*) AS cnt
            FROM bookings b
            JOIN services s ON s.id = b.service_id
            WHERE b.status = 'active'
              AND strftime('%Y-%m', b.created_at) = strftime('%Y-%m', 'now', 'localtime')
            GROUP BY b.service_id
            ORDER BY cnt DESC
            LIMIT 1
            """
        )
        popular_row = await cursor.fetchone()
        popular = popular_row["name"] if popular_row else None

        cursor = await db.execute(
            """
            SELECT COUNT(DISTINCT user_id) AS cnt FROM bookings
            WHERE status = 'active'
              AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now', 'localtime')
            """
        )
        unique_clients = (await cursor.fetchone())["cnt"]

        return AdminStats(
            total_bookings=total,
            popular_service=popular,
            unique_clients=unique_clients,
        )
