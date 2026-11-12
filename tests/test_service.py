import service


def test_run_cycle_calls_notifier(monkeypatch):
    result = service.CycleResult(counts={"market": 3}, alerts=["один", "два"])
    monkeypatch.setattr(service, "collect_signals", lambda: result)

    sent = []
    output = service.run_cycle(notifier=sent.append)

    assert sent == ["один", "два"]
    assert output is result


def test_run_cycle_without_notifier(monkeypatch):
    result = service.CycleResult(counts={}, alerts=["x"])
    monkeypatch.setattr(service, "collect_signals", lambda: result)

    assert service.run_cycle() is result


def test_collect_signals_returns_counts(monkeypatch):
    monkeypatch.setattr(service.market_collector, "collect", lambda tracked: 4)
    monkeypatch.setattr(service.rss_collector, "collect", lambda aliases: 3)
    monkeypatch.setattr(service.cryptopanic_collector, "collect", lambda tracked: 2)
    monkeypatch.setattr(service.reddit_collector, "collect", lambda aliases: 0)
    monkeypatch.setattr(service.feargreed_collector, "fetch", dict)
    monkeypatch.setattr(service.alert_engine, "check_alerts", lambda tracked: ["alert"])

    result = service.collect_signals(aliases={"BTC": ["btc"]})

    assert result.counts == {"market": 4, "rss": 3, "cryptopanic": 2, "reddit": 0}
    assert result.alerts == ["alert"]


def test_tracked_set_is_built_from_aliases(monkeypatch):
    seen = {}

    def fake_market_collect(tracked):
        seen["tracked"] = tracked
        return 0

    monkeypatch.setattr(service.market_collector, "collect", fake_market_collect)
    monkeypatch.setattr(service.rss_collector, "collect", lambda aliases: 0)
    monkeypatch.setattr(service.cryptopanic_collector, "collect", lambda tracked: 0)
    monkeypatch.setattr(service.reddit_collector, "collect", lambda aliases: 0)
    monkeypatch.setattr(service.feargreed_collector, "fetch", dict)
    monkeypatch.setattr(service.alert_engine, "check_alerts", lambda tracked: [])

    service.collect_signals(aliases={"BTC": ["btc"], "ETH": ["eth"]})

    assert seen["tracked"] == {"BTC", "ETH"}


def test_probe_exchanges_delegates_to_collector(monkeypatch):
    monkeypatch.setattr(service.market_collector, "probe", lambda: {"bybit": True})

    assert service.probe_exchanges() == {"bybit": True}
