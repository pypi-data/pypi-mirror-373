from collections.abc import Callable

from zapper import SORTING_CHOICES

class Zapper[Target_Type]:
    def __init__(
        self,
        *,
        source_input: str | tuple[str, ...],
        src: str,
        replace: str = "",
        split_count: int = 0,
        sep: str | None = None,
        func: Callable[[str], Target_Type] = ...,  # type: ignore[type-arg]
        strict: bool = True,
        regex: bool = False,
        atomic: bool = True,
        filter_start: bool = False,
        filter_end: bool = False,
        sorting: SORTING_CHOICES = "length",
    ) -> None: ...
    def zap_as_type(
        self,
        *,
        source_input: str | tuple[str, ...],
        src: str,
        replace: str = "",
        split_count: int = 0,
        sep: str | None = None,
        func: Callable[[str], Target_Type] = ...,
        strict: bool = True,
        regex: bool = False,
        atomic: bool = True,
        filter_start: bool = False,
        filter_end: bool = False,
        sorting: SORTING_CHOICES = "length",
    ) -> tuple[Target_Type, ...]: ...
