import json

import pandas as pd
import pytest
import sqlalchemy as sa

from KonoPyUtil import command_query, data_query, get_engine, write_dataframe
from KonoPyUtil.exceptions import MissingCredentialsError

CREDS = {"DBNAME": "db", "USERID": "u", "PASSWORD": "p", "HOST": "h", "PORT": "5432"}


@pytest.fixture
def sqlite_engine(tmp_path):
    engine = sa.create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    yield engine
    engine.dispose()


# ---- get_engine -------------------------------------------------------------


def _write_dot_env(directory, creds=CREDS):
    (directory / ".env").write_text(f"DB_CREDENTIALS='{json.dumps(creds)}'\n")


def test_get_engine_builds_psycopg2_url(in_tmp_dir):
    # regression: SQLAlchemy>=2.1 defaults postgresql:// to psycopg (v3)
    _write_dot_env(in_tmp_dir)
    engine = get_engine()
    try:
        assert engine.dialect.driver == "psycopg2"
        assert str(engine.url) == "postgresql+psycopg2://u:***@h:5432/db"
        assert engine.url.password == "p"
    finally:
        engine.dispose()


def test_get_engine_without_credentials_raises(in_tmp_dir):
    with pytest.raises(MissingCredentialsError):
        get_engine()


def test_get_engine_uses_explicit_credentials():
    # regression: get_engine(credentials=...) previously ignored its argument (UnboundLocalError)
    engine = get_engine(credentials=CREDS)
    try:
        assert engine.dialect.driver == "psycopg2"
        assert str(engine.url) == "postgresql+psycopg2://u:***@h:5432/db"
    finally:
        engine.dispose()


# ---- data_query / command_query / write_dataframe (SQLite, no network) -------


def test_write_then_query_round_trip(sqlite_engine):
    df = pd.DataFrame({"team": ["A", "B"], "elo": [1000.5, 1010.0]})
    assert write_dataframe(df, "ratings", engine=sqlite_engine) is True

    result = data_query("SELECT team, elo FROM ratings ORDER BY team", engine=sqlite_engine)
    pd.testing.assert_frame_equal(result, df)


def test_write_dataframe_replaces_table(sqlite_engine):
    write_dataframe(pd.DataFrame({"x": [1]}), "t", engine=sqlite_engine)
    write_dataframe(pd.DataFrame({"x": [2, 3]}), "t", engine=sqlite_engine, if_exists="replace")
    assert list(data_query("SELECT x FROM t ORDER BY x", engine=sqlite_engine)["x"]) == [2, 3]


def test_write_dataframe_returns_false_on_failure(sqlite_engine):
    bad = pd.DataFrame({"x": [{"not": "storable"}]})
    assert write_dataframe(bad, "broken", engine=sqlite_engine) is False


def test_command_query_executes_statement(sqlite_engine):
    write_dataframe(pd.DataFrame({"x": [1, 2, 3]}), "t", engine=sqlite_engine)
    command_query("DELETE FROM t WHERE x > 1", engine=sqlite_engine)
    assert len(data_query("SELECT * FROM t", engine=sqlite_engine)) == 1
