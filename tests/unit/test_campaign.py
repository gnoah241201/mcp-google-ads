"""Tests for campaign tools.

Note: Full integration tests require a working google-ads package.
These tests focus on validation logic and dry_run behavior.
"""

import pytest
from unittest.mock import MagicMock, patch

# Import once at module level
from mcp_google_ads.tools.campaign import set_campaign_status, update_campaign


class TestSetCampaignStatus:
    def test_validate_only_true_by_default(self):
        """Test that dry_run=True (validate_only=True) is the default."""
        with patch("mcp_google_ads.tools.campaign.get_client") as mock_client:
            mock_gads = MagicMock()
            mock_client.return_value = mock_gads
            mock_gads.get_service().mutate_campaigns.return_value = MagicMock(results=[])

            with patch("mcp_google_ads.safety._execute") as mock_exec:
                def execute_side_effect(fn):
                    fn()  # Run the do_mutate function
                    return MagicMock(results=[])
                mock_exec.side_effect = execute_side_effect

                set_campaign_status("1234567890", "cam123", "PAUSED")

                # Verify validate_only is True in the call
                call_args = mock_gads.get_service().mutate_campaigns.call_args
                assert call_args is not None
                kwargs = call_args[1]
                assert kwargs.get("validate_only") is True

    def test_validate_only_false_when_dry_run_false(self):
        """Test that dry_run=False passes validate_only=False to the API."""
        with patch("mcp_google_ads.tools.campaign.get_client") as mock_client:
            mock_gads = MagicMock()
            mock_client.return_value = mock_gads
            mock_gads.get_service().mutate_campaigns.return_value = MagicMock(results=[])

            with patch("mcp_google_ads.safety._execute") as mock_exec:
                def execute_side_effect(fn):
                    fn()  # Run the do_mutate function
                    return MagicMock(results=[])
                mock_exec.side_effect = execute_side_effect

                set_campaign_status("1234567890", "cam123", "PAUSED", dry_run=False)

                # Verify validate_only is False in the call
                call_args = mock_gads.get_service().mutate_campaigns.call_args
                assert call_args is not None, "mutate_campaigns should have been called"
                kwargs = call_args[1]
                assert kwargs.get("validate_only") is False


class TestUpdateCampaign:
    def test_rejects_unknown_fields(self):
        """Test that update_campaign validates allowed fields."""
        with pytest.raises(ValueError, match="Unknown fields"):
            update_campaign("1234567890", "cam123", {"invalid_field": "value"})
