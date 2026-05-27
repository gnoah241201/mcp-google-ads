import pytest
from mcp_google_ads.auth import normalize_customer_id, ValidationError


class TestNormalizeCustomerId:
    def test_strips_dashes(self):
        assert normalize_customer_id("123-456-7890") == "1234567890"

    def test_strips_spaces(self):
        assert normalize_customer_id("123 456 7890") == "1234567890"

    def test_passes_through_plain_digits(self):
        assert normalize_customer_id("1234567890") == "1234567890"

    def test_rejects_short_id(self):
        with pytest.raises(ValidationError, match="10 digits"):
            normalize_customer_id("123456789")

    def test_rejects_long_id(self):
        with pytest.raises(ValidationError, match="10 digits"):
            normalize_customer_id("12345678901")

    def test_rejects_non_digits(self):
        with pytest.raises(ValidationError, match="digits"):
            normalize_customer_id("123456789A")

    def test_rejects_empty(self):
        with pytest.raises(ValidationError):
            normalize_customer_id("")