import pytest
from unittest.mock import MagicMock, patch


class TestCreateResponsiveSearchAd:
    def test_validate_only_true_by_default(self):
        with patch("mcp_google_ads.client.get_client") as mock_client:
            mock_gads = MagicMock()
            mock_client.return_value = mock_gads
            mock_gads.get_service().mutate_ad_group_ads.return_value = MagicMock(results=[])
            with patch("mcp_google_ads.safety._execute") as mock_exec:
                mock_exec.return_value = MagicMock(results=[])
                from mcp_google_ads.tools.ad import create_responsive_search_ad
                create_responsive_search_ad(
                    "1234567890", "ag123",
                    headlines=["Shoes Sale", "Buy Shoes", "Best Shoes"],
                    descriptions=["Great deals on shoes", "Free shipping"],
                    final_urls=["https://example.com/shoes"],
                )
                call_kwargs = mock_gads.get_service().mutate_ad_group_ads.call_args.kwargs
                assert call_kwargs["validate_only"] is True
