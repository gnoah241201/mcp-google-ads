import pytest
from unittest.mock import MagicMock, patch, call


class TestSearchAds:
    def test_normalizes_customer_id(self):
        with patch("mcp_google_ads.auth.normalize_customer_id") as mock_norm:
            mock_norm.side_effect = lambda cid: cid.replace("-", "")
            with patch("mcp_google_ads.client.get_client") as mock_client:
                mock_gads = MagicMock()
                mock_client.return_value = mock_gads
                mock_gads.get_service().search.return_value = iter([])
                from mcp_google_ads.tools.read import search_ads
                search_ads("123-456-7890", "SELECT campaign.id FROM campaign")
                mock_norm.assert_called_once_with("123-456-7890")


class TestListAccessibleCustomers:
    def test_no_params(self):
        with patch("mcp_google_ads.client.get_client") as mock_client:
            mock_gads = MagicMock()
            mock_client.return_value = mock_gads
            mock_gads.get_service().list_accessible_customers.return_value = iter([])
            from mcp_google_ads.tools.read import list_accessible_customers
            result = list_accessible_customers()
            assert isinstance(result, list)


class TestListCampaigns:
    def test_returns_structured_list(self):
        # Patch _execute at the module level where read.py imports it
        with patch("mcp_google_ads.tools.read._execute") as mock_exec:
            mock_row = MagicMock()
            mock_row.campaign.id = "123"
            mock_row.campaign.name = "Test Campaign"
            mock_row.campaign.status.name = "ENABLED"
            mock_row.campaign.budget.amount_micros = "50000000"
            mock_exec.return_value = iter([mock_row])

            from mcp_google_ads.tools.read import list_campaigns
            result = list_campaigns("1234567890")
            assert len(result) == 1
            assert result[0]["id"] == "123"
            assert result[0]["status"] == "ENABLED"