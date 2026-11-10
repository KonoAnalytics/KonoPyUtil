import os

import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def _isolate_credential_env(monkeypatch):
    """set_credentials() writes to os.environ; snapshot and restore the variables it touches."""
    for name in ("DB_CREDENTIALS", "IPINFO_CREDENTIALS"):
        monkeypatch.delenv(name, raising=False)
    yield
    for name in ("DB_CREDENTIALS", "IPINFO_CREDENTIALS"):
        os.environ.pop(name, None)


@pytest.fixture
def in_tmp_dir(tmp_path, monkeypatch):
    """Run the test from an empty directory so no real .env file is picked up."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def elo_games():
    """Four games between three teams, in the format get_elo_season expects."""
    return pd.DataFrame(
        {
            "match": [1, 2, 3, 4],
            "game_time": ["2024-01-01", "2024-01-08", "2024-01-15", "2024-01-22"],
            "home_name": ["A", "B", "A", "C"],
            "away_name": ["B", "C", "C", "A"],
            "home_score": [2, 1, 0, 3],
            "away_score": [1, 1, 2, 0],
        }
    )
