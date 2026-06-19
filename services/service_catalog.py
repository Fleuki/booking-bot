from models.database import get_connection
from models.service import Service


class ServiceCatalog:
    async def get_all(self) -> list[Service]:
        db = await get_connection()
        cursor = await db.execute(
            "SELECT * FROM services ORDER BY id"
        )
        rows = await cursor.fetchall()
        return [Service.from_row(row) for row in rows]

    async def get_by_id(self, service_id: int) -> Service | None:
        db = await get_connection()
        cursor = await db.execute(
            "SELECT * FROM services WHERE id = ?",
            (service_id,),
        )
        row = await cursor.fetchone()
        return Service.from_row(row) if row else None
