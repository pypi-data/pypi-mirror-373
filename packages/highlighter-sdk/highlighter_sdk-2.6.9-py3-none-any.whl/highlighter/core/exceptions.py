class OptionalPackageMissingError(Exception):
    def __init__(self, package_name, option_name):
        super().__init__(f"{package_name} not found. Use pip install highlighter-sdk[{option_name}]")


def require_package(package, package_name, option_name):
    """
    Decorator that checks if a specific module is available before running a function.

    :param module: The module to check (should be None if not imported).
    :param module_name: The name of the module as a string.
    :raises OptionalImportException: If the module is not available.
    """
    packages = package if isinstance(package, (list, tuple)) else [package]
    package_names = package_name if isinstance(package_name, (list, tuple)) else [package_name]
    option_names = option_name if isinstance(option_name, (list, tuple)) else [option_name]

    def decorator(func):
        def wrapper(*args, **kwargs):
            for m, pn, on in zip(packages, package_names, option_names):
                if m is None:
                    raise OptionalPackageMissingError(pn, on)
            return func(*args, **kwargs)

        return wrapper

    return decorator
