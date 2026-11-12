import pytest

from jobradar.companies import ConfigError, load_companies, load_feeds


def test_load_companies_rejects_invalid_entry(tmp_path):
    cfg = tmp_path / "companies.yaml"
    cfg.write_text("companies: [bad]\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_companies(cfg)


def test_load_feeds_rejects_unknown_feed(tmp_path):
    cfg = tmp_path / "companies.yaml"
    cfg.write_text("feeds: [ghost]\ncompanies: []\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_feeds(cfg)
