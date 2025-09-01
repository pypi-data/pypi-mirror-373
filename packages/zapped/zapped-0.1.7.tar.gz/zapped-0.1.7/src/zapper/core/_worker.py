"""A over-engineered string symbol remover :D."""

from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Literal, Self, overload

from zapper._common import SORTING_CHOICES
from zapper._funcs import clean, clean_seps, convert, process_patterns, tuple_parse
from zapper.config import ZapConfig


@dataclass(slots=True)
class ZapWorker:
    result_str: str = field(default="")
    result_tuple: tuple[str, ...] = field(default_factory=tuple)
    last_value_: str = field(default="result_str")

    @property
    def store_result(self) -> str | tuple[str, ...]:
        raise NotImplementedError("Use the setter to store results. Write-only property.")

    @store_result.setter
    def store_result(self, value: str | tuple[str, ...]) -> None:
        if isinstance(value, str):
            self.result_str = value
            self.last_value_ = "result_str"
        if isinstance(value, tuple):
            self.result_tuple = value
            self.last_value_ = "result_tuple"

    def get_value(self) -> str | tuple[str, ...]:
        return getattr(self, self.last_value_)


class ZapHandler[Target_Type]:
    """A class to remove specified symbols from a source string."""

    def __init__(self, config: ZapConfig) -> None:
        """Initialize the Zapper with symbols, source string, and optional parameters."""
        self.config: ZapConfig[Target_Type] = config
        self.worker = ZapWorker()
        self.operators: list[partial] = []

    def _add_operator(self, operator: Callable, **kwargs) -> None:
        """Add an operator with its parameters to the operators list."""
        self.operators.append(partial(operator, **kwargs))

    @property
    def value(self) -> str:
        """Return the modified source string."""
        return self.worker.result_str

    @property
    def unpacked(self) -> tuple[Any, ...]:
        """Return the unpacked values as a tuple."""
        return self.worker.result_tuple

    def remove_symbols(self, **kwargs) -> Self:
        """Remove specified symbols from the source string."""
        cfg: ZapConfig[Target_Type] = self.config.update_from_args(**kwargs) or self.config
        patterns: list[str] = process_patterns(src=cfg.source_input, atomic=cfg.atomic, sorting=cfg.sorting)
        f_end: bool = cfg.filter_end
        f_start: bool = cfg.filter_start
        self._add_operator(operator=clean, source=cfg.src, patterns=patterns, replace=cfg.replace, regex=cfg.regex)
        self._add_operator(operator=clean_seps, sep=cfg.sep, filter_start=f_start, filter_end=f_end, strict=cfg.strict)
        return self

    def remove_to_tuple(self, **kwargs) -> Self:
        """Remove specified symbols and return a tuple of unpacked values."""
        cfg: ZapConfig[Target_Type] = self.config.update_from_args(**kwargs) or self.config
        patterns: list[str] = process_patterns(src=cfg.source_input, atomic=cfg.atomic, sorting=cfg.sorting)
        f_end: bool = cfg.filter_end
        f_start: bool = cfg.filter_start
        self._add_operator(operator=clean, source=cfg.src, patterns=patterns, replace=cfg.replace, regex=cfg.regex)
        self._add_operator(operator=clean_seps, sep=cfg.sep, filter_start=f_start, filter_end=f_end, strict=cfg.strict)
        self._add_operator(operator=tuple_parse, split_count=cfg.split_count, sep=cfg.sep, strict=cfg.strict)
        return self

    def convert_as_type(self, **kwargs) -> Self:
        """Convert the result in self.result to the specified type."""
        cfg: ZapConfig[Target_Type] = self.config.update_from_args(**kwargs) or self.config
        self._add_operator(operator=convert, converter_func=cfg.func)
        return self

    @overload
    def do(self, string: Literal[True] = True) -> str: ...

    @overload
    def do(self, string: Literal[False]) -> tuple[Target_Type, ...]: ...

    def do(self, string: bool = False) -> str | tuple[Target_Type, ...]:
        """Execute all added operations in sequence."""
        for operator in self.operators:
            self.worker.store_result = operator(data=self.worker.get_value())
        self.operators.clear()
        return self.value if string else self.unpacked

    @classmethod
    def from_args(
        cls,
        source_input: str | tuple[str, ...],
        src: str,
        replace: str = "",
        split_count: int = 0,
        sep: str | None = None,
        func: Callable[[str], Target_Type] = str,
        strict: bool = True,
        regex: bool = False,
        filter_start: bool = False,
        filter_end: bool = False,
        atomic: bool = True,
        sorting: SORTING_CHOICES = "length",
    ) -> Self:
        """Create a Zapper instance from configuration parameters.

        Args:
            source_input: Symbols to remove (string or tuple of strings)
            src: Source string to process
            replace: String to replace removed symbols with
            split_count: Expected number of items to unpack (0 for any)
            sep: Separator used to split the modified source string
            func: Type to convert unpacked items to (e.g., int, float, str)
            strict: If True, enforce exact unpack count
            regex: If True, treat symbols as regex patterns
            filter_start: Remove separator from start before parsing
            filter_end: Remove separator from end before parsing
            atomic: If True, treat each string as a whole pattern; if False, each char as a pattern
            sorting: Sorting method for patterns ('length' or 'none')

        Returns:
            A configured Zapper instance.
        """
        config: ZapConfig[Target_Type] = ZapConfig(
            source_input=source_input,
            src=src,
            replace=replace,
            split_count=split_count,
            sep=sep if sep is not None else replace or ".",
            func=func,
            strict=strict,
            regex=regex,
            filter_start=filter_start,
            filter_end=filter_end,
            atomic=atomic,
            sorting=sorting,
        )
        return cls(config)


__all__ = ["ZapHandler"]
