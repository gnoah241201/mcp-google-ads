"""Tests for ad_group tools.

Note: Full integration tests require a working google-ads package.
These tests focus on validation logic that can be tested without API mocking.
"""

import pytest


class TestUpdateAdGroup:
    def test_rejects_unknown_fields(self):
        """Test that update_ad_group validates allowed fields."""
        from mcp_google_ads.tools.ad_group import update_ad_group

        with pytest.raises(ValueError, match="Unknown fields"):
            update_ad_group("1234567890", "ag123", {"invalid_field": "value"})

    def test_rejects_multiple_unknown_fields(self):
        """Test that multiple unknown fields are reported."""
        from mcp_google_ads.tools.ad_group import update_ad_group

        with pytest.raises(ValueError, match="Unknown fields"):
            update_ad_group("1234567890", "ag123", {"foo": 1, "bar": 2})

    def test_allows_known_fields(self):
        """Test that known fields (name, status, cpc_bid_micros) pass validation."""
        from mcp_google_ads.tools.ad_group import update_ad_group
        import sys
        from unittest.mock import MagicMock, patch

        # These fields should NOT raise ValueError for field validation
        allowed_fields = ["name", "status", "cpc_bid_micros"]

        for field in allowed_fields:
            try:
                # Try to call with the field
                # We expect either success or errors from mocking, not ValueError
                with patch("mcp_google_ads.client.get_client"):
                    update_ad_group("1234567890", "ag123", {field: "test_value"})
            except ValueError as e:
                if "Unknown fields" in str(e):
                    pytest.fail(f"Field '{field}' should be allowed but was rejected")
                raise
            except (ModuleNotFoundError, AttributeError):
                # google-ads import/mocking issue - field validation passed
                pass
