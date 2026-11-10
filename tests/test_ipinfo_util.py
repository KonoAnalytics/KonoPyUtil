import json
from types import SimpleNamespace

import pandas as pd
import pytest

from KonoPyUtil import ipinfo_util


def _details(ip="8.8.8.8", **overrides):
    data = {
        "ip": ip,
        "city": "Austin",
        "region": "Texas",
        "country": "US",
        "country_name": "United States",
        "postal": "78701",
        "latitude": "30.2672",
        "longitude": "-97.7431",
        "timezone": "America/Chicago",
        "loc": "30.2672,-97.7431",
        "country_currency": {"code": "USD", "symbol": "$"},
        "country_flag": {"emoji": "🇺🇸", "unicode": "U+1F1FA"},
        "continent": {"code": "NA", "name": "North America"},
    }
    data.update(overrides)
    return data


@pytest.fixture
def fake_ipinfo(monkeypatch, in_tmp_dir):
    """Replaces the ipinfo client and captures what geocode_ip would write to the database."""
    (in_tmp_dir / ".env").write_text('IPINFO_CREDENTIALS=\'{"TOKEN": "test-token"}\'\n')
    state = {"details": _details(), "written": None, "tokens": []}

    class FakeHandler:
        def getDetails(self, ip_address):
            return SimpleNamespace(all=dict(state["details"]))

    def fake_get_handler(token):
        state["tokens"].append(token)
        return FakeHandler()

    def fake_write(df, tablename, if_exists="append", **kwargs):
        state["written"] = df
        return True

    monkeypatch.setattr(ipinfo_util.ipinfo, "getHandler", fake_get_handler)
    monkeypatch.setattr(ipinfo_util, "write_dataframe", fake_write)
    monkeypatch.setattr(ipinfo_util, "data_query", lambda query: pd.DataFrame())
    return state


def test_validate_ip_address():
    assert ipinfo_util._validate_ip_address("8.8.8.8") is True
    assert ipinfo_util._validate_ip_address("2001:4860:4860::8888") is True
    assert ipinfo_util._validate_ip_address("999.1.1.1") is False
    assert ipinfo_util._validate_ip_address("not an ip") is False


def test_geocode_rejects_malformed_ip_without_network(fake_ipinfo):
    result = ipinfo_util.geocode_ip("999.1.1.1", use_cache=False)
    assert result == {"Success": "False", "Message": "Improperly Formatted IP Address"}
    assert fake_ipinfo["tokens"] == []


def test_geocode_uses_ipinfo_token_from_credentials(fake_ipinfo):
    ipinfo_util.geocode_ip("8.8.8.8", use_cache=False)
    assert fake_ipinfo["tokens"] == ["test-token"]


def test_geocode_returns_location_and_writes_row(fake_ipinfo):
    result = ipinfo_util.geocode_ip("8.8.8.8", use_cache=False)
    assert result["Success"] == "True"
    assert result["ip_address"] == "8.8.8.8"
    assert result["stateCode"] == "TX"
    assert result["continentCode"] == "NA"
    assert result["countryCode"] == "US"
    assert result["latitude"] == pytest.approx(30.2672)
    written = fake_ipinfo["written"]
    assert len(written) == 1
    assert "country_flag" not in written.columns
    assert "loc" not in written.columns


def test_geocode_reports_bogon_address(fake_ipinfo):
    fake_ipinfo["details"] = {"ip": "10.0.0.1", "bogon": True}
    result = ipinfo_util.geocode_ip("10.0.0.1", use_cache=False)
    assert result == {"Success": "False", "Message": "Can't locate IP Address"}
    assert fake_ipinfo["written"] is None


def test_geocode_returns_cached_row_without_calling_ipinfo(monkeypatch, fake_ipinfo):
    cached = pd.DataFrame([{"ip_address": "8.8.8.8", "stateCode": "TX"}])
    monkeypatch.setattr(ipinfo_util, "data_query", lambda query: cached)
    result = ipinfo_util.geocode_ip("8.8.8.8", use_cache=True)
    assert result["Success"] == "True"
    assert result["stateCode"] == "TX"
    assert fake_ipinfo["tokens"] == []
