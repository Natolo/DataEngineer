import pytest

from retail_ingestion.validation import is_present, validate_sale


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        ("", False),
        ("   ", False),
        ("S001", True),
    ],
)
def test_param_is_present(value: str | None, expected: bool,) -> None:
    assert is_present(value) is expected

@pytest.fixture
def valid_sale() -> dict[str, str]:
    return {
        "sale_id": "S001",
        "sale_date": "2026-09-20",
        "amount": "19.90",
    }
@pytest.mark.parametrize(
    ("field", "invalid_value", "expected_error"),
    [
        ("sale_id", "", "Missing sale_id"),
        ("amount", "-10.00", "Invalid amount"),
        ("amount", "NaN", "Invalid amount"),
        ("amount", "Infinity", "Invalid amount"),
    ],
)
def test_invalid_sale(
    valid_sale: dict[str, str],
    field: str,
    invalid_value: str,
    expected_error: str,
) -> None:
    sale = valid_sale.copy()
    sale[field] = invalid_value
    is_valid, errors = validate_sale(sale)
    assert not is_valid
    assert expected_error in errors

def test_valid_sale(valid_sale: dict[str, str]) -> None:
    result = validate_sale(valid_sale)

    assert result == (True, [])