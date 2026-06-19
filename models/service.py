from dataclasses import dataclass


@dataclass(slots=True)
class Service:
    id: int
    name: str
    description: str
    price: float
    duration_minutes: int

    @classmethod
    def from_row(cls, row) -> "Service":
        return cls(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            price=row["price"],
            duration_minutes=row["duration_minutes"],
        )

    def format_card(self) -> str:
        return (
            f"<b>{self.name}</b>\n"
            f"{self.description}\n\n"
            f"💰 {self.price:.0f} ₽ · ⏱ {self.duration_minutes} мин."
        )
