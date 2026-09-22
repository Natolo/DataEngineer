from datetime import datetime

class InvalidDatetimeError(ValueError):
    pass


def is_present(input_string: str | None) -> bool:
    return not (input_string is None or input_string.strip() == "")


def parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise InvalidDatetimeError(f"Invalid datetime format: {value}") from error