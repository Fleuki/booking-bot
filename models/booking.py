from dataclasses import dataclass
from datetime import datetime

from utils.datetime_utils import format_date_display


@dataclass(slots=True)
class Booking:
    id: int
    user_id: int
    client_name: str
    service_id: int
    booking_date: str
    booking_time: str
    status: str
    reminder_sent: bool = False
    created_at: datetime | None = None
    service_name: str | None = None

    @classmethod
    def from_row(cls, row) -> "Booking":
        keys = row.keys()
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            client_name=row["client_name"],
            service_id=row["service_id"],
            booking_date=row["booking_date"],
            booking_time=row["booking_time"],
            status=row["status"],
            reminder_sent=bool(row["reminder_sent"]),
            created_at=row["created_at"],
            service_name=row["service_name"] if "service_name" in keys else None,
        )

    def format_short(self) -> str:
        service = self.service_name or f"Услуга #{self.service_id}"
        return (
            f"#{self.id} · {service}\n"
            f"📅 {format_date_display(self.booking_date)} в {self.booking_time}\n"
            f"👤 {self.client_name}"
        )
