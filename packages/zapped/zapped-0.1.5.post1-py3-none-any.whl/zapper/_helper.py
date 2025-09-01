from collections.abc import Callable

from zapper._common import SORTING_CHOICES
from zapper.core._worker import ZapHandler


def zap(*sym: str, src: str, replace: str = "", atomic: bool | None = None) -> str:
    """Remove specified symbols from the source string.

    Args:
        sym: Single string or multiple strings containing symbols to remove
        src: The source string from which to remove the symbols
        replace: The string to replace the removed symbols with
        atomic: If True, treat each string as whole pattern; if False, split into chars
               Defaults to False for single string, True for multiple strings

    Returns:
        str: The modified source string with specified symbols removed.

    Examples:
        >>> zap("!?*", "Hello!? World! *")  # Single string, chars mode
        'Hello World '
        >>> zap("://", "/", src="https://example.com/path")  # Multiple strings, atomic mode
        'httpsexample.compath'
    """
    zapper: ZapHandler[str] = ZapHandler.from_args(
        source_input=sym[0] if len(sym) == 1 else sym,
        src=src,
        replace=replace,
        atomic=len(sym) > 1 if atomic is None else atomic,
        strict=False,
    )
    return zapper.remove_symbols().do(string=True)


def zap_get[Target_Type](
    *sym: str,
    src: str,
    split_count: int = -1,
    replace: str = "",
    sep: str | None = None,
    atomic: bool | None = None,
    strict: bool = True,
) -> tuple[Target_Type, ...]:  # type: ignore[type-arg]
    """Remove specified symbols from the source string and return a tuple of unpacked values.

    Args:
        *sym: A variable number of strings containing symbols to remove from src (e.g., "?!" or "!?")
        src (str): The source string from which to remove the symbols
        split_count (int): The expected number of items to unpack from the result if strict mode is enabled.
        replace (str, optional): The string to replace the removed symbols with (default is an empty string).
        sep (str, optional): The separator used to split the modified source string (default is ".").
        atomic (bool, optional): If True, treat each string as a whole pattern; if False, each char as a pattern.
                                 Defaults to False for single string, True for multiple strings.

    Returns:
        tuple[str, ...]: A tuple of unpacked values from the modified source string.

    Raises:
        ValueError: If the number of items in the result does not match split_count.
    """
    try:
        return (
            ZapHandler.from_args(
                source_input=sym[0] if len(sym) == 1 else sym,
                src=src,
                replace=replace,
                split_count=split_count,
                sep=sep,
                strict=strict,
                atomic=len(sym) > 1 if atomic is None else atomic,
            )
            .remove_to_tuple()
            .do(string=False)
        )
    except Exception as e:
        raise ValueError(f"Error unpacking values: {e}") from e


def zap_as[Target_Type](
    *sym: str,
    src: str,
    split_count: int,
    replace: str = "",
    sep: str | None = None,
    func: Callable[[str], Target_Type] = str,
    strict: bool = True,
    regex: bool = False,
    filter_start: bool = False,  # Will filter out any separators at the start of the string
    filter_end: bool = False,  # Will filter out any separators at the end of the string
    atomic: bool | None = None,  # If True, treat the input symbols as a single string to replace
    sorting: SORTING_CHOICES = "length",
) -> tuple[Target_Type, ...]:
    """Remove specified symbols from the source string, unpack the result, and convert it to a specified type.

    Args:
        sym (str): A string containing symbols to remove from src (e.g., "?!" or "!?")
        src (str): The source string from which to remove the symbols
        split_count (int): The expected number of items to unpack from the result
        replace (str, optional): The string to replace the removed symbols with (default is an empty string).
        sep (str, optional): The separator used to split the modified source string (default is ".").
        func (type, optional): The type of the result to cast/convert to (default is str).

    Returns:
        ZapHandler: An instance of the ZapHandler class configured with the provided parameters.
    """
    try:
        return (
            ZapHandler[Target_Type]
            .from_args(
                source_input=sym[0] if len(sym) == 1 else sym,
                src=src,
                replace=replace,
                split_count=split_count,
                sep=sep,
                func=func,
                strict=strict,
                regex=regex,
                filter_start=filter_start,
                filter_end=filter_end,
                atomic=atomic if atomic is not None else (len(sym) > 1),
                sorting=sorting,
            )
            .remove_to_tuple()
            .convert_as_type()
            .do(string=False)
        )
    except Exception as e:
        raise ValueError(f"Error converting values: {e}") from e
