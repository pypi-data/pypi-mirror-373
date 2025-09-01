import re


def replace_forward_slash_with_underscore(filename):
    if filename is None:
        return None

    invalid_chars = r"[/]"
    sanitized = re.sub(invalid_chars, "_", filename)
    return sanitized


def stringify_if_not_null(attribute):
    return str(attribute) if attribute is not None else None
