import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.booking import send_booking_reminders

logger = logging.getLogger(__name__)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    async def reminder_job() -> None:
        try:
            await send_booking_reminders(bot)
        except Exception:
            logger.exception("Reminder job failed")

    scheduler.add_job(
        reminder_job,
        trigger="interval",
        minutes=15,
        id="booking_reminders",
        replace_existing=True,
    )
    return scheduler
