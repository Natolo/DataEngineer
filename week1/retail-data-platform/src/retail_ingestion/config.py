import os


class InvalidConfigurationError(ValueError):
    pass


def check_reject_limit(reject_limit: int) -> None:
    if reject_limit < 0:
        raise InvalidConfigurationError("Reject limit cannot be negative")


def get_reject_limit() -> int:
    raw_value = os.getenv("RETAIL_REJECT_LIMIT", "10")
    try:
        reject_limit = int(raw_value)
    except ValueError as error:
        raise InvalidConfigurationError(
            f"Invalid reject limit: {raw_value}"
        ) from error

    check_reject_limit(reject_limit)
    return reject_limit