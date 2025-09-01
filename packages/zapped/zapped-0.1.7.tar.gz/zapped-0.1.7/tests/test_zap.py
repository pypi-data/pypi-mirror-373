from zapper import zap


class TestZap:
    def test_zap(self) -> None:
        """Test the zap function for symbol removal and replacement."""
        assert zap("!?", src="Hello!? World") == "Hello World"
        assert zap("!", src="Hello! World! Test!") == "Hello World Test"
        assert zap("-+", src="1.2.3-alpha+build", replace=".") == "1.2.3.alpha.build"

        test_version = "v2.1.4-beta.3+build-2024.01.15_hotfix!urgent"
        expected = "v2.1.4.beta.3.build.2024.01.15.hotfix.urgent"
        assert zap("-+._!", src=test_version, replace=".") == expected

        assert zap("!@#", src="test!@#data@#!end", replace="_") == "test___data___end"
        assert zap("123", src="a1b2c3d") == "abcd"

    def test_zap_edge_cases(self) -> None:
        """Test edge cases and special scenarios."""
        assert zap("!@", src="test!!@@data", replace="_") == "test____data"
        assert zap(".", src="1.2.3", replace=".") == "1.2.3"
        assert zap("★☆", src="Hello★World☆Test", replace="-") == "Hello-World-Test"
        assert zap("123", src="version1.2.3", replace=".") == "version....."
        assert zap("xyz", src="Hello World") == "Hello World"  # No symbols found
        assert zap("!?", src="") == ""  # Empty string
        assert zap("Hello", src="Hello") == ""  # Remove entire string
