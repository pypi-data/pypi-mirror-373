from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any, TypeVar, cast, get_args, get_origin

from zapper._helper import zap_as

Target_Type = TypeVar("Target_Type")


@dataclass
class ParamInfo:
    param: type | Annotated
    inner_types: tuple[Any, ...]
    tuple_length: int


def extract_tuple_info(param: type | Annotated) -> ParamInfo:
    """Extract tuple types from an Annotated type. Dead simple version."""
    metadata = get_args(param)

    if get_origin(param) is Annotated:
        metadata = get_args(param)[1:]
        for meta in metadata:
            if get_origin(meta) is tuple:
                inner_types = get_args(meta)
                return ParamInfo(param=param, inner_types=inner_types, tuple_length=len(inner_types))
    else:
        for meta in metadata:
            if get_origin(meta) is tuple:
                inner_types = get_args(meta)
                return ParamInfo(param=param, inner_types=inner_types, tuple_length=len(inner_types))
    return ParamInfo(param=param, inner_types=metadata, tuple_length=len(metadata))


def smart_parse_version(version_str: str) -> tuple[int, int, int] | tuple[int, int, int, str]:
    """Auto-detect version format and return properly typed tuple."""
    parts: tuple[str, ...] = zap_as(".-_", src=version_str, split_count=-3, replace=".")
    three_parts: int = len((0, 0, 0))
    four_parts: int = len((0, 0, 0, ""))
    if len(parts) == three_parts:
        return cast("tuple[int, int, int]", zap_as(".-", src=version_str, split_count=3, func=int, replace="."))
    if len(parts) == four_parts:
        nums = zap_as(".-", src=version_str, split_count=3, func=int, replace=".")
        label = version_str.split("-")[-1]  # Get the label part
        return cast("tuple[int, int, int, str]", (*nums, label))
    raise ValueError("Unsupported version format")


if __name__ == "__main__":
    # ruff: noqa: S101
    version_str = "1.9.1-beta"
    output = smart_parse_version(version_str=version_str)
    assert output == (1, 9, 1, "beta")
    assert isinstance(output, tuple)
    assert all(isinstance(x, (int | str)) for x in output)
    version_str = "1.9.1"
    output = smart_parse_version(version_str=version_str)
    assert output == (1, 9, 1)
    assert isinstance(output, tuple)
    assert all(isinstance(x, int) for x in output)
    version_str = "2.0.0-alpha.1+build123"
    output = smart_parse_version(version_str=version_str)
    assert output == (2, 0, 0, "alpha.1+build123")
    assert isinstance(output, tuple)
    # print(ver_tuple, type(ver_tuple))
    # version_list = []
    # for i, t in enumerate(types):
    #     print(i, t)
    #     version_list.append(t(ver_tuple[i]))
    # print(version_list)
    # for version in version_list:
    #     print(version, type(version))
