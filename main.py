import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
import db
import service
from bot import bot, dp, send_alert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("futures-bot.main")


async def collect_and_check():
    result = service.collect_signals()

    logger.info(
        "Собрано сигналов: market=%d rss=%d cryptopanic=%d reddit=%d",
        result.counts.get("market", 0),
        result.counts.get("rss", 0),
        result.counts.get("cryptopanic", 0),
        result.counts.get("reddit", 0),
    )

    for text in result.alerts:
        await send_alert(text)
        logger.info("Отправлен алерт: %s", text.splitlines()[0])


async def main():
    db.init_db()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        collect_and_check,
        "interval",
        seconds=config.COLLECT_INTERVAL_SECONDS,
        next_run_time=None,
    )
    scheduler.start()

    # первый сбор сразу при старте, не дожидаясь первого интервала
    await collect_and_check()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
