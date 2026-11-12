from datetime import datetime, timedelta


def add_signal(db, coin="BTC", source="rss", category="news",
               direction="up", text="заголовок", url="https://example.com/1"):
    db.insert_signal(coin, source, category, direction, text, url)


def test_insert_and_read_signal(temp_db):
    add_signal(temp_db)

    rows = temp_db.get_recent_signals("BTC", 20)

    assert len(rows) == 1
    assert rows[0]["coin"] == "BTC"
    assert rows[0]["direction"] == "up"
    assert rows[0]["category"] == "news"


def test_duplicate_source_and_url_is_ignored(temp_db):
    add_signal(temp_db, url="https://example.com/same")
    add_signal(temp_db, url="https://example.com/same")

    assert len(temp_db.get_recent_signals("BTC", 20)) == 1


def test_same_url_from_different_source_is_kept(temp_db):
    add_signal(temp_db, source="rss", url="https://example.com/x")
    add_signal(temp_db, source="cryptopanic", url="https://example.com/x")

    assert len(temp_db.get_recent_signals("BTC", 20)) == 2


def test_old_signals_fall_out_of_window(temp_db):
    add_signal(temp_db)
    old = (datetime.utcnow() - timedelta(days=2)).isoformat()
    with temp_db.get_conn() as conn:
        conn.execute("UPDATE signals SET created_at = ?", (old,))

    assert temp_db.get_recent_signals("BTC", 20) == []


def test_tracked_coins_are_unique(temp_db):
    add_signal(temp_db, coin="BTC", url="https://example.com/a")
    add_signal(temp_db, coin="BTC", url="https://example.com/b")
    add_signal(temp_db, coin="ETH", url="https://example.com/c")

    assert sorted(temp_db.get_tracked_coins()) == ["BTC", "ETH"]


def test_alert_state_roundtrip(temp_db):
    assert temp_db.get_last_alert_time("BTC") is None

    temp_db.set_last_alert_time("BTC")

    assert temp_db.get_last_alert_time("BTC") is not None


def test_prune_removes_stale_signals(temp_db):
    add_signal(temp_db)
    old = (datetime.utcnow() - timedelta(hours=100)).isoformat()
    with temp_db.get_conn() as conn:
        conn.execute("UPDATE signals SET created_at = ?", (old,))

    temp_db.prune_old(signal_hours=48)

    with temp_db.get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) AS n FROM signals").fetchone()["n"]
    assert count == 0


def test_snapshot_near_returns_latest(temp_db):
    temp_db.insert_market_snapshot("BTC", "bybit", 60000.0, 0.01, 1000.0)

    row = temp_db.get_snapshot_near("BTC", "bybit", minutes_ago=1)

    assert row is not None
    assert row["price"] == 60000.0
