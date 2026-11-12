import alert_engine

_counter = [0]


def add_signal(db, category, direction, coin="BTC"):
    """Добавляет сигнал с уникальным url, чтобы не сработала дедупликация."""
    _counter[0] += 1
    db.insert_signal(
        coin,
        f"src-{_counter[0]}",
        category,
        direction,
        f"текст сигнала {_counter[0]}",
        f"https://example.com/{_counter[0]}",
    )


def test_alert_when_two_categories_agree(temp_db, thresholds):
    add_signal(temp_db, "market", "up")
    add_signal(temp_db, "news", "up")
    add_signal(temp_db, "news", "up")

    alerts = alert_engine.check_alerts(["BTC"])

    assert len(alerts) == 1
    assert "BTC" in alerts[0]
    assert "market" in alerts[0]
    assert "news" in alerts[0]
    assert "Fear & Greed Index" in alerts[0]


def test_single_category_is_not_enough(temp_db, thresholds):
    add_signal(temp_db, "market", "up")

    assert alert_engine.check_alerts(["BTC"]) == []


def test_opposite_directions_do_not_alert(temp_db, thresholds):
    add_signal(temp_db, "market", "up")
    add_signal(temp_db, "news", "down")
    add_signal(temp_db, "news", "down")

    assert alert_engine.check_alerts(["BTC"]) == []


def test_news_below_ratio_is_ignored(temp_db, thresholds):
    add_signal(temp_db, "market", "up")
    add_signal(temp_db, "news", "up")
    add_signal(temp_db, "news", "down")

    assert alert_engine.check_alerts(["BTC"]) == []


def test_news_below_min_signals_is_ignored(temp_db, thresholds):
    add_signal(temp_db, "market", "up")
    add_signal(temp_db, "news", "up")

    assert alert_engine.check_alerts(["BTC"]) == []


def test_cooldown_blocks_repeated_alert(temp_db, thresholds):
    add_signal(temp_db, "market", "up")
    add_signal(temp_db, "news", "up")
    add_signal(temp_db, "news", "up")

    first = alert_engine.check_alerts(["BTC"])
    second = alert_engine.check_alerts(["BTC"])

    assert len(first) == 1
    assert second == []


def test_coin_without_signals_is_skipped(temp_db, thresholds):
    add_signal(temp_db, "market", "up", coin="ETH")
    add_signal(temp_db, "news", "up", coin="ETH")
    add_signal(temp_db, "news", "up", coin="ETH")

    alerts = alert_engine.check_alerts(["BTC"])

    assert alerts == []
