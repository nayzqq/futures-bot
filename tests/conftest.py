import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
import db


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Подменяет файл базы на временный и создаёт схему."""
    monkeypatch.setattr(config, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    return db


@pytest.fixture
def thresholds(monkeypatch):
    """Низкие пороги, чтобы алерт было проще воспроизвести в тесте."""
    monkeypatch.setattr(
        config,
        "CATEGORY_THRESHOLDS",
        {
            "market": {"min_signals": 1, "ratio": 0.5},
            "news": {"min_signals": 2, "ratio": 0.6},
            "social": {"min_signals": 5, "ratio": 0.65},
        },
    )
