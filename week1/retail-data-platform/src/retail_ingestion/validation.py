from datetime import datetime
from decimal import Decimal, InvalidOperation


class InvalidDatetimeError(ValueError):
    pass


class InvalidAmountError(ValueError):
    pass


def is_present(input_string: str | None) -> bool:
    return not (input_string is None or input_string.strip() == "")


def parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise InvalidDatetimeError(f"Invalid datetime format: {value}") from error


def parse_amount(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as error:
        raise InvalidAmountError(f"Invalid amount format: {value}") from error


def validate_sale(sale: dict[str, str]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not is_present(sale.get("sale_date")):
        errors.append("Missing sale_date")
    else:
        try:
            parse_datetime(sale["sale_date"])
        except InvalidDatetimeError:
            errors.append("Invalid datetime")

    if not is_present(sale.get("amount")):
        errors.append("Missing amount")
    else:
        try:
            amount = parse_amount(sale["amount"])
            if not amount.is_finite() or amount <= 0:
                errors.append("Invalid amount")
        except InvalidAmountError:
            errors.append("Invalid amount")

    if not is_present(sale.get("sale_id")):
        errors.append("Missing sale_id")
    return len(errors) == 0, errors