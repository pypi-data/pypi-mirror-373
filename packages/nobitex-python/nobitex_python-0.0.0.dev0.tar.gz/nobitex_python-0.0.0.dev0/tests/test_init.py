"""Test for nobitex package."""

import nobitex


class TestVersion:
    """Test for nobitex.__version__."""

    def test_version(self):
        """Test for nobitex.__version__."""
        assert nobitex.__version__ is not None
