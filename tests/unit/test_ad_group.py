import sys
from unittest.mock import MagicMock, patch

import pytest


# Create mock v21 module to avoid broken google-ads imports
mock_v21 = MagicMock()
sys.modules["google.ads.googleads.v21"] = mock_v21
sys.modules["google.ads.googleads.v21.resources"] = mock_v21.resources
sys.modules["google.ads.googleads.v21.resources.types"] = mock_v21.resources.types
sys.modules["google.ads.googleads.v21.services"] = mock_v21.services
sys.modules["google.ads.googleads.v21.services.types"] = mock_v21.services.types
sys.modules["google.ads.googleads.v21.enums"] = mock_v21.enums
sys.modules["google.ads.googleads.v21.enums.types"] = mock_v21.enums.types
sys.modules["google.ads.googleads.v21.types"] = mock_v21.types


class TestSetAdGroupStatus:
    def test_validate_only_true_by_default(self):
        with patch("mcp_google_ads.client.get_client") as mock_client:
            mock_gads = MagicMock()
            mock_client.return_value = mock_gads
            mock_gads.get_service().mutate_ad_groups.return_value = MagicMock(results=[])
            with patch("mcp_google_ads.safety._execute") as mock_exec:
                mock_exec.return_value = MagicMock(results=[])
                from mcp_google_ads.tools.ad_group import set_ad_group_status
                set_ad_group_status("1234567890", "ag123", "PAUSED")
                call_kwargs = mock_gads.get_service().mutate_ad_groups.call_args.kwargs
                assert call_kwargs["validate_only"] is True


class TestUpdateAdGroup:
    def test_rejects_unknown_fields(self):
        with pytest.raises(ValueError, match="Unknown fields"):
            from mcp_google_ads.tools.ad_group import update_ad_group
            update_ad_group("1234567890", "ag123", {"invalid_field": "value"})
