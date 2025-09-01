import hashlib
import re


def sha512_of_content(content):
    sha512 = hashlib.sha512()
    sha512.update(content)
    return sha512.hexdigest()


def get_slug(name) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def stringify_if_not_null(attribute):
    return str(attribute) if attribute is not None else None
