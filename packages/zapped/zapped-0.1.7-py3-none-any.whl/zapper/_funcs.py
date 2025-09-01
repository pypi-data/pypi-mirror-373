from collections.abc import Callable
import re

from zapper._common import SORTING_CHOICES

# ruff: noqa: ARG001


def tuple_parse(split_count: int, sep: str, strict: bool, data: str) -> tuple[str, ...]:
    """Parse text into a tuple of string parts.

    Args:
        data: Text to parse

    Returns:
        Tuple of string parts

    Raises:
        ValueError: If strict=True and part count doesn't match expected
    """
    if split_count > 0:
        parts: list[str] = data.split(sep)[:split_count]
    else:
        parts = data.split(sep)
    if strict and split_count > 0 and len(parts) != split_count:
        raise ValueError(f"Expected {split_count} items, got {len(parts)}: {parts}")
    return tuple(parts)


def clean_seps(sep: str, filter_start: bool, filter_end: bool, strict: bool, data: str) -> str:
    """Apply separator filtering and cleanup.

    Args:
        data: The text to clean
        sep: The separator string to filter
        filter_start: If True, remove sep from start of text
        filter_end: If True, remove sep from end of text
        strict: If True, replace multiple consecutive seps with a single sep

    Returns:
        The cleaned text
    """
    text: str = data
    if filter_start and text.startswith(sep):
        text = text[len(sep) :]
    if filter_end and text.endswith(sep):
        text = text[: -len(sep)]
    if strict:
        text = text.replace(sep * 2, sep)
    return text


def clean(source: str, patterns: list[str], replace: str, regex: bool, data: str) -> str:
    """Clean the text by removing/replacing patterns.

    Args:
        source: The source text to clean
        patterns: List of patterns to remove/replace
        replace: The string to replace the patterns with
        regex: If True, treat patterns as regex; if False, as plain strings
        data: Unused parameter for compatibility with operator functions

    Returns:
        The cleaned text with patterns replaced
    """
    result: str = source
    for pattern in patterns:
        result = re.sub(pattern, replace, result) if regex else result.replace(pattern, replace)
    return result


def convert[Target_Type](
    data: tuple[str, ...],
    converter_func: Callable[[str], Target_Type],
) -> tuple[Target_Type, ...]:
    """Convert tuple of strings to tuple of target type.

    Args:
        string_tuple: Tuple of strings to convert

    Returns:
        Tuple of converted values

    Raises:
        ValueError: If conversion fails for any item
    """
    if not data:
        raise ValueError("No items to convert. Tuple is empty.")
    try:
        converted_items: list[Target_Type] = []
        for item in data:
            converted_items.append(converter_func(item))
        return tuple(converted_items)
    except Exception as e:
        raise ValueError(f"Error converting items: {e}") from e


def process_patterns(src: str | tuple[str, ...], atomic: bool, sorting: SORTING_CHOICES) -> list[str]:
    """Process the input patterns based on atomic mode.

    Args:
        src: The input patterns as a string or tuple of strings
        atomic: If True, treat the entire string/tuple as single patterns; if False, split into individual characters
        sorting: The method to sort the patterns ("length" or "order")

    Returns:
        A list of processed patterns that are unique and sorted
    """
    if src == "":
        return []
    patterns_to_use: list[str] = []
    if isinstance(src, str):
        patterns_to_use = string_work(atomic, patterns_to_use, src)
    if isinstance(src, tuple):
        patterns_to_use = tuple_work(atomic, patterns_to_use, src)
    return dedupe(atomic, sorting, patterns_to_use)


def string_work(atomic: bool, patterns_to_use: list[str], patterns: str) -> list[str]:
    if not atomic:
        patterns_to_use.extend([char for char in patterns if char])
    else:
        patterns_to_use.append(patterns)
    return patterns_to_use


def tuple_work(atomic: bool, patterns_to_use: list[str], patterns: tuple[str, ...]) -> list[str]:
    if not atomic:
        for pattern in patterns:
            patterns_to_use.extend([char for char in pattern if char])
    else:
        patterns_to_use.extend([pattern for pattern in patterns if pattern])
    return patterns_to_use


def dedupe(atomic: bool, sorting: SORTING_CHOICES, strings: list[str]) -> list[str]:
    """Remove duplicates and sort patterns.

    Args:
        strings: List of patterns to deduplicate and sort

    Returns:
        A list of unique patterns, sorted based on the specified method
    """
    if atomic and sorting == "length":
        return sorted(set(strings), key=len, reverse=True)

    seen: set[str] = set()
    result: list[str] = []
    for pattern in strings:
        if pattern not in seen:
            seen.add(pattern)
            result.append(pattern)
    return result
