from datetime import date, datetime, timedelta

DATE_INPUT_FORMATS = ("%d.%m.%Y", "%d.%m.%y")
TIME_INPUT_FORMAT = "%H:%M"
DATE_DISPLAY_FORMAT = "%d.%m.%Y"
DATE_STORAGE_FORMAT = "%Y-%m-%d"


def parse_date(text: str) -> date | None:
    text = text.strip()
    for fmt in DATE_INPUT_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_time(text: str) -> datetime | None:
    text = text.strip()
    try:
        return datetime.strptime(text, TIME_INPUT_FORMAT)
    except ValueError:
        return None


def format_date_storage(d: date) -> str:
    return d.strftime(DATE_STORAGE_FORMAT)


def format_date_display(date_str: str) -> str:
    try:
        d = datetime.strptime(date_str, DATE_STORAGE_FORMAT).date()
        return d.strftime(DATE_DISPLAY_FORMAT)
    except ValueError:
        return date_str


def booking_datetime(date_str: str, time_str: str) -> datetime | None:
    try:
        return datetime.strptime(
            f"{date_str} {time_str}",
            f"{DATE_STORAGE_FORMAT} {TIME_INPUT_FORMAT}",
        )
    except ValueError:
        return None


def is_future_booking(date_str: str, time_str: str) -> bool:
    dt = booking_datetime(date_str, time_str)
    return dt is not None and dt > datetime.now()


def today_storage() -> str:
    return date.today().strftime(DATE_STORAGE_FORMAT)


def week_ahead_storage() -> str:
    return (date.today() + timedelta(days=7)).strftime(DATE_STORAGE_FORMAT)
