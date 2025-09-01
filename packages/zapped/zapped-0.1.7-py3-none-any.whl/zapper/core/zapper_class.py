"""The main class for the zapper module."""

from zapper import zap_as
from zapper.core._worker import ZapHandler

# TODO: Return to this class and finish it.


class Zapper[Target_Type]:
    """A class that is the swiss army knife of strings, replace symbols, replace substrings, and return as any type you want."""

    def __init__(self, *sym, **kwargs) -> None:
        """Initialize the Zapper with symbols and parameters."""
        self.zapper: ZapHandler[Target_Type] = ZapHandler[Target_Type].from_args(source_input=sym, **kwargs)

    def zap_to_type(self, *sym: str, **kwargs) -> None:
        """Zap the symbols to the desired type."""
        store_result: tuple[Target_Type, ...] = zap_as(*sym, **kwargs)
        print(store_result)

    # TODO: Finish this class
