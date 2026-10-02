"""Docent: contract analytics (classify, extract, ask)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("docent")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
