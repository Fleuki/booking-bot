from pathlib import Path

import aiosqlite

_connection: aiosqlite.Connection | None = None

SEED_SERVICES = (
    (
        "Стрижка мужская",
        "Классическая или модельная стрижка с укладкой",
        1200,
        45,
    ),
    (
        "Стрижка женская",
        "Стрижка любой сложности с мытьём и укладкой",
        2500,
        60,
    ),
    (
        "Маникюр",
        "Классический маникюр с покрытием гель-лаком",
        1800,
        90,
    ),
    (
        "Окрашивание волос",
        "Окрашивание в один тон или тонирование",
        4500,
        120,
    ),
    (
        "Массаж спины",
        "Расслабляющий массаж спины и шеи",
        2000,
        40,
    ),
)


async def init_db(db_path: Path) -> None:
    global _connection

    db_path.parent.mkdir(parents=True, exist_ok=True)
    _connection = await aiosqlite.connect(db_path)
    _connection.row_factory = aiosqlite.Row

    await _connection.execute(
        """
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            duration_minutes INTEGER NOT NULL
        )
        """
    )

    await _connection.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            client_name TEXT NOT NULL,
            service_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            reminder_sent INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_id) REFERENCES services (id)
        )
        """
    )

    await _migrate_bookings_table()
    await _seed_services()
    await _connection.commit()


async def _migrate_bookings_table() -> None:
    cursor = await _connection.execute("PRAGMA table_info(bookings)")
    columns = {row["name"] for row in await cursor.fetchall()}

    if not columns:
        return

    if "service_id" not in columns:
        await _connection.execute(
            "ALTER TABLE bookings ADD COLUMN service_id INTEGER"
        )
        await _connection.execute(
            "UPDATE bookings SET service_id = 1 WHERE service_id IS NULL"
        )

    if "reminder_sent" not in columns:
        await _connection.execute(
            "ALTER TABLE bookings ADD COLUMN reminder_sent INTEGER NOT NULL DEFAULT 0"
        )


async def _seed_services() -> None:
    cursor = await _connection.execute("SELECT COUNT(*) AS cnt FROM services")
    row = await cursor.fetchone()
    if row["cnt"] > 0:
        return

    await _connection.executemany(
        """
        INSERT INTO services (name, description, price, duration_minutes)
        VALUES (?, ?, ?, ?)
        """,
        SEED_SERVICES,
    )


async def get_connection() -> aiosqlite.Connection:
    if _connection is None:
        raise RuntimeError("Database is not initialized. Call init_db() first.")
    return _connection
