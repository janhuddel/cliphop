import pytest

from cliphop.config import Config, parse_duration


@pytest.mark.parametrize(
    ("text", "expected"),
    [("24h", 86400), ("30m", 1800), ("45", 45), ("7d", 604800), ("10s", 10), (" 2h ", 7200)],
)
def test_parse_duration(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "1x", "-5h", "1.5h"])
def test_parse_duration_rejects_invalid(text):
    with pytest.raises(ValueError):
        parse_duration(text)


def test_config_defaults():
    config = Config.from_env({})
    assert config.db_path == "/data/cliphop.db"
    assert config.ttl_seconds == 24 * 3600
    assert config.max_items == 50
    assert config.base_url == "https://cliphop.rohwer.sh"


def test_config_from_env_overrides():
    config = Config.from_env(
        {
            "CLIPHOP_DB": ":memory:",
            "CLIPHOP_TTL": "30m",
            "CLIPHOP_MAX_ITEMS": "5",
            "BASE_URL": "http://localhost:8000",
        }
    )
    assert config.db_path == ":memory:"
    assert config.ttl_seconds == 1800
    assert config.max_items == 5
    assert config.base_url == "http://localhost:8000"
