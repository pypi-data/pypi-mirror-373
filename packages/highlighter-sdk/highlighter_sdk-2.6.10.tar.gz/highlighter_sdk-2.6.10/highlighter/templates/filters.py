import re

from cookiecutter.utils import simple_filter

__all__ = ["camel_to_snake"]


@simple_filter
def camel_to_snake(name):
    name = str(name)
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
