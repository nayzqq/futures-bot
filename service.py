"""
Сервисный слой: один цикл сбора сигналов и проверки алертов.

Модуль не знает, как именно доставляются уведомления: он принимает функцию
notifier, поэтому его можно использовать и в консольном запуске (run_once.py),
и в тестах с заглушкой вместо Telegram.
"""
import logging
from dataclasses import dataclass, field

import alert_engine
import config
import markets
from collectors import (
    cryptopanic_collector,
    feargreed_collector,
    market_collector,
    reddit_collector,
    rss_collector,
)

logger = logging.getLogger("futures-bot.service")


@dataclass
class CycleResult:
    """Итог одного цикла: сколько сигналов собрано и какие алерты найдены."""

    counts: dict = field(default_factory=dict)
    alerts: list = field(default_factory=list)


def probe_exchanges() -> dict:
    """Проверяет доступность бирж с текущего IP (для диагностики в логах)."""
    return market_collector.probe()


def collect_signals(aliases: dict | None = None,
                    tracked: set | None = None) -> CycleResult:
    """Собирает данные из всех источников и проверяет условия алертов."""
    if aliases is None:
        aliases = markets.get_top10_aliases(fallback=config.COIN_ALIASES)
    if tracked is None:
        tracked = set(aliases.keys())

    counts = {
        "market": market_collector.collect(tracked),
        "rss": rss_collector.collect(aliases),
        "cryptopanic": cryptopanic_collector.collect(tracked),
        "reddit": reddit_collector.collect(aliases),
    }
    feargreed_collector.fetch()

    alerts = alert_engine.check_alerts(sorted(tracked))
    return CycleResult(counts=counts, alerts=alerts)


def run_cycle(notifier=None) -> CycleResult:
    """Полный цикл: собрать -> проверить -> отдать алерты в notifier."""
    result = collect_signals()
    if notifier is not None:
        for text in result.alerts:
            notifier(text)
    return result
