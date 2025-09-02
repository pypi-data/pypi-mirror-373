def str_to_bool(value: str) -> bool:
    """
    Convert a string to a boolean value.

    :param value: The string to convert.
    :return: Must be one of "yes", "true", or "1" to return True.
    """
    return value.lower() in ("yes", "true", "1")
