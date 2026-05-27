"""GoogleAdsClient singleton, loaded once from environment."""

from google.ads.googleads.client import GoogleAdsClient

_client: GoogleAdsClient | None = None


def get_client() -> GoogleAdsClient:
    """Return cached GoogleAdsClient. Creates it from env vars on first call."""
    global _client
    if _client is None:
        _client = GoogleAdsClient.load_from_env()
    return _client


def reset_client() -> None:
    """Reset the cached client. Used in tests."""
    global _client
    _client = None
