import pytest
from retail_ingestion.config import get_reject_limit, InvalidConfigurationError


def test_default_reject_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("RETAIL_REJECT_LIMIT", raising=False)
    assert get_reject_limit() == 10


def test_reject_limit_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETAIL_REJECT_LIMIT", "25")
    assert get_reject_limit() == 25


@pytest.mark.parametrize(
    "invalid_value",
    ["abc", "-1", "1.5"],
)
def test_invalid_reject_limit(monkeypatch: pytest.MonkeyPatch, invalid_value: str,) -> None:
    monkeypatch.setenv("RETAIL_REJECT_LIMIT", invalid_value)
    with pytest.raises(InvalidConfigurationError):
        get_reject_limit()
