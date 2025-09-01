from pathlib import Path

import pytest

from zapper import zap, zap_as


class TestZapAs:
    def test_zap_as_int(self):
        """Test the zap_as function for type conversion."""
        result = zap_as("-+", src="1.2.3-alpha", split_count=3, replace=".", sep=".", func=int)
        assert result == (1, 2, 3)
        assert all(isinstance(x, int) for x in result)

    def test_zap_as_float(self):
        """Test float conversion with coordinate data."""
        result = zap_as(",;", src="1.5,2.7;3.9", split_count=3, replace="|", sep="|", func=float)
        assert result == (1.5, 2.7, 3.9)
        assert all(isinstance(x, float) for x in result)

    def test_zap_as_str(self):
        result = zap_as("-+", src="hello-world.test", split_count=3, replace=".", sep=".", func=str)
        assert result == ("hello", "world", "test")
        assert all(isinstance(x, str) for x in result)

    def test_zap_as_custom_types(self):
        def to_upper(s: str) -> str:
            return s.upper()

        result = zap_as("-_", src="hello-world_test", split_count=3, replace=".", sep=".", func=to_upper)
        assert result == ("HELLO", "WORLD", "TEST")

        result = zap_as("!", src="1!2!3", split_count=3, replace=".", sep=".", func=lambda x: int(x) * 2)
        assert result == (2, 4, 6)

    def test_zap_as_path(self):
        sym = ";"
        result = zap_as(sym, src="/home;/tmp;/var", split_count=3, replace=sym, sep=sym, func=Path)
        assert all(isinstance(x, Path) for x in result)
        assert result[0] == Path("/home")

    def test_zap_as_bool(self):
        result = zap_as(",", src="True,False,1", split_count=3, replace="|", sep="|", func=bool)
        assert result == (True, True, True)  # bool("False") is True!

    def test_zap_as_custom_converter(self):
        def safe_int(s: str) -> int:
            try:
                return int(s)
            except ValueError:
                return 0

        result: tuple[int, ...] = zap_as("-", src="1-bad-3", split_count=3, replace=".", func=safe_int)
        assert result == (1, 0, 3)

    def test_zap_str_as_number(self):
        with pytest.raises(ValueError):
            zap_as("-", src="1-two-3", split_count=3, replace=".", func=int)  # "two" can't convert to int

    def test_zap_as_invalid_input(self):
        with pytest.raises(ValueError):
            zap_as("-", src="1-2", split_count=3, replace=".", sep="-", func=int, strict=True)  # Only 2 items, need 3

    def test_zap_as_empty_string(self):
        with pytest.raises(ValueError):
            zap_as("-", src="", split_count=3, replace=".", sep="-", func=int, strict=True)

    def test_zap_as_custom_converter_with_length(self):
        def custom_converter(s: str) -> dict:
            return {"value": s, "length": len(s)}

        result = zap_as("-", src="a-bb-ccc", split_count=3, replace=".", func=custom_converter)
        expected = ({"value": "a", "length": 1}, {"value": "bb", "length": 2}, {"value": "ccc", "length": 3})
        assert result == expected

    def test_zap_as_version_parsing(self):
        major, minor, patch = zap_as("-+", src="1.2.3-beta+build", split_count=3, replace=".", sep=".", func=int)
        assert (major, minor, patch) == (1, 2, 3)
        assert all(isinstance(x, int) for x in (major, minor, patch))


class TestZapAsMulti:
    """Testing passing in multiple strings as automatic replacement values."""

    def test_zap_as_url(self):
        starting_string = "https://example.com/path"
        protocol, domain, path = zap_as("://", "/", src=starting_string, split_count=3, replace=",", func=str)
        assert (protocol, domain, path) == ("https", "example.com", "path")

    def test_zap_as_multi_with_custom_func(self):
        def custom_func(s: str) -> str:
            return s.upper()

        result: tuple[str, ...] = zap_as("-", "/", ".", src="a-b/c.d", split_count=4, replace=",", func=custom_func)
        assert result == ("A", "B", "C", "D")
        assert all(isinstance(x, str) for x in result)

    def test_zap_as_multi_order_matters(self):
        """Test that replacement order affects results."""
        # Order matters: replace "abc" first vs "ab" first
        result1: tuple[str, ...] = zap_as("abc", "ab", src="abcdef", split_count=2, replace=",", sorting="order")
        result2: tuple[str, ...] = zap_as("ab", "abc", src="abcdef", split_count=2, replace=",", sorting="order")
        assert result1 != result2

        # if we do it by length, they should be the same
        result1 = zap_as("abc", "ab", src="abcdef", split_count=2, replace=",", sorting="length")
        result2 = zap_as("ab", "abc", src="abcdef", split_count=2, replace=",", sorting="length")
        assert result1 == result2

    def test_zap_as_multi_overlapping_patterns(self):
        """Test overlapping patterns don't interfere."""
        result: tuple[str, ...] = zap_as("//", "/", src="https://example.com//path", split_count=3, replace=",")
        assert len(result) == 3

    def test_zap_as_multi_empty_patterns(self):
        """Test behavior with empty patterns."""
        result: tuple[str, ...] = zap_as("", "//", src="https://example.com", split_count=2, replace="|")
        assert result == ("https:", "example.com")

    def test_zap_as_multi_complex_separators(self):
        """Test with complex multi-character separators."""
        data = "item1::sep::item2::sep::item3"
        result: tuple[str, ...] = zap_as("::sep::", ".", src=data, split_count=3, replace=",")
        assert result == ("item1", "item2", "item3")

    def test_zap_as_multi_nested_patterns(self):
        """Test patterns that contain other patterns."""
        result = zap_as("()", "(", ")", src="(a)(b)(c)", split_count=3, replace=",", filter_start=True)
        assert result == ("a", "b", "c")

    def test_zap_as_multi_int_conversion(self) -> None:
        """Test multi-pattern with int conversion."""
        version_string = "v1.2.3-beta+build"
        result_string: str = zap("v", src=version_string)
        major, minor, patch = zap_as("-", "+", src=result_string, split_count=3, replace=".", func=int)
        assert (major, minor, patch) == (1, 2, 3)

    def test_zap_as_multi_regex_mode(self):
        """Test multi-pattern with regex enabled."""
        result: tuple[str, ...] = zap_as(r"\d+", r"[a-z]+", src="123abc456def", split_count=2, replace="|", regex=True)
        # Should handle regex patterns correctly

    def test_zap_as_multi_no_matches(self):
        """Test when patterns don't exist in source."""
        result: tuple[str, ...] = zap_as("xyz", "123", src="hello world", split_count=1, replace="|")
        assert result == ("hello world",)

    def test_zap_as_multi_case_sensitivity(self):
        """Test case-sensitive pattern matching."""
        result: tuple[str, ...] = zap_as("HTTP", "://", src="https://example.com", split_count=2, replace="|")
        assert result == ("https", "example.com")
