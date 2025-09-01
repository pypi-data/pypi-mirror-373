"""
Tests for the core functionality.
"""

import pytest
from ai_kill_switch.core import hello


class TestCore:
    """Test cases for core functionality."""
    
    def test_hello(self):
        """Test the hello function returns the expected message."""
        result = hello()
        expected = "Hello from AI Kill Switch!"
        assert result == expected
        assert isinstance(result, str)
