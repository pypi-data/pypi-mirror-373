from importlib.metadata import version as get_installed_version

__all__ = ["__version__"]

try:
    __version__ = get_installed_version("highlighter-sdk")
except Exception as e:
    __version__ = "unable to determine version, see the pyproject.toml"
