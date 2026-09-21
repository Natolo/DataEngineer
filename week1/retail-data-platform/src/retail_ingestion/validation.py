def is_present(input_string: str | None) -> bool:
    return not (input_string is None or input_string.strip() == "")