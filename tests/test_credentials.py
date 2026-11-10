import json
import os

from KonoPyUtil import set_credentials

CREDS = {"DBNAME": "db", "USERID": "u", "PASSWORD": "p", "HOST": "h", "PORT": "5432"}


def _write_env(path, var_name, value):
    path.write_text(f"{var_name}='{json.dumps(value)}'\n")


def test_reads_credentials_from_env_file(tmp_path):
    env_file = tmp_path / "custom.env"
    _write_env(env_file, "DB_CREDENTIALS", CREDS)
    assert set_credentials(str(env_file), recurse=False) == CREDS


def test_populates_os_environ(tmp_path):
    # regression: environs>=12 kept values off os.environ, breaking set_credentials
    env_file = tmp_path / "custom.env"
    _write_env(env_file, "DB_CREDENTIALS", CREDS)
    set_credentials(str(env_file), recurse=False)
    assert json.loads(os.environ["DB_CREDENTIALS"]) == CREDS


def test_file_overrides_existing_environment_variable(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_CREDENTIALS", json.dumps({"USERID": "stale"}))
    env_file = tmp_path / "custom.env"
    _write_env(env_file, "DB_CREDENTIALS", CREDS)
    assert set_credentials(str(env_file), recurse=False)["USERID"] == "u"


def test_missing_file_returns_empty_dict(tmp_path):
    assert set_credentials(str(tmp_path / "nope.env"), recurse=False) == {}


def test_custom_variable_name(tmp_path):
    env_file = tmp_path / "custom.env"
    _write_env(env_file, "IPINFO_CREDENTIALS", {"TOKEN": "abc"})
    result = set_credentials(str(env_file), env_var_name="IPINFO_CREDENTIALS", recurse=False)
    assert result == {"TOKEN": "abc"}


def test_no_file_argument_uses_existing_environment(monkeypatch):
    monkeypatch.setenv("DB_CREDENTIALS", json.dumps(CREDS))
    assert set_credentials(None) == CREDS


def test_no_file_and_no_environment_returns_empty_dict():
    assert set_credentials(None) == {}


def test_default_path_reads_dot_env_in_cwd(in_tmp_dir):
    _write_env(in_tmp_dir / ".env", "DB_CREDENTIALS", CREDS)
    assert set_credentials() == CREDS
