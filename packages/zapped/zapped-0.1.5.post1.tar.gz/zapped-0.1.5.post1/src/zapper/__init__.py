"""Zapper package.

A string manipulation tool for crazed maniacs including built in typed tuple returns.
"""

from zapper._internal.cli import main
from zapper._internal.debug import _METADATA

__version__: str = _METADATA.version

from zapper._common import SORTING_CHOICES
from zapper._helper import zap, zap_as, zap_get

__all__: list[str] = ["SORTING_CHOICES", "_METADATA", "__version__", "main", "zap", "zap_as", "zap_get"]
