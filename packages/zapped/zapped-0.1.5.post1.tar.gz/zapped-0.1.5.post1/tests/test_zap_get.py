import pytest

from zapper import zap_get


class TestZapGet:
    def test_zap_get(self):
        """Test the zap_get function for version string parsing."""
        assert zap_get("-+", src="1.2.3-alpha", split_count=3, replace=".") == ("1", "2", "3")
        assert zap_get("-+", src="1.2.3+build", split_count=3, replace=".") == ("1", "2", "3")
        assert zap_get("-+", src="1.2.3-alpha", split_count=2, replace=".") == ("1", "2")
        assert zap_get("-+", src="1.2.3-alpha", split_count=4, replace=".") == ("1", "2", "3", "alpha")

        # Complex version strings
        assert zap_get("-+._", src="v1.2.3-beta.4+build_123", split_count=4, replace=".") == ("v1", "2", "3", "beta")

        # Edge cases
        assert zap_get("", src="1.2.3", split_count=3) == ("1", "2", "3")
        assert zap_get("-", src="1-2-3", split_count=3, replace=".") == ("1", "2", "3")

        with pytest.raises(ValueError):
            zap_get("-+", src="invalid", split_count=3, replace=".")

        with pytest.raises(ValueError):
            zap_get("-+", src="", split_count=3, replace=".")  # Empty string

    def test_version_parsing_scenarios(self):
        """Test realistic version string scenarios."""
        assert zap_get("-+", src="1.0.0", split_count=3, replace=".") == ("1", "0", "0")
        assert zap_get("-+", src="2.1.4-beta", split_count=3, replace=".") == ("2", "1", "4")
        assert zap_get("-+", src="1.2.3+20240115", split_count=3, replace=".") == ("1", "2", "3")
        assert zap_get("-+", src="1.0.0-alpha.1+build.123", split_count=3, replace=".") == ("1", "0", "0")
        assert zap_get(".-+", src="1.2.3.post1", split_count=3, replace=".") == ("1", "2", "3")
        assert zap_get(".-+", src="2.0.0.dev1+build", split_count=3, replace=".") == ("2", "0", "0")
        assert zap_get("-+", src="v1.2.3-rc1", split_count=4, replace=".") == ("v1", "2", "3", "rc1")
