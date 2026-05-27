import pytest
from unittest.mock import patch, MagicMock
from mcp_google_ads.client import get_client, reset_client


class TestGetClient:
    def test_returns_google_ads_client_instance(self):
        reset_client()
        with patch("google.ads.googleads.client.GoogleAdsClient.load_from_env") as mock_load:
            mock_load.return_value = MagicMock()
            client = get_client()
            assert client is not None
            mock_load.assert_called_once()

    def test_caches_client(self):
        reset_client()
        with patch("google.ads.googleads.client.GoogleAdsClient.load_from_env") as mock_load:
            mock_load.return_value = MagicMock()
            client1 = get_client()
            client2 = get_client()
            assert client1 is client2
            assert mock_load.call_count == 1
