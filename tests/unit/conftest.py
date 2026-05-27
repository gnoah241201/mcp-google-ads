"""Global test fixtures and mock setup for google-ads v21."""

import sys
from unittest.mock import MagicMock


def _setup_google_ads_mocks():
    """Set up mock v21 modules to work around broken package imports."""
    # Create the module hierarchy as MagicMock objects
    mock_types = MagicMock()
    mock_resources_types = MagicMock()
    mock_services_types = MagicMock()
    mock_enums_types = MagicMock()
    mock_types_types = MagicMock()
    mock_services_services = MagicMock()

    # Set up the nested structure
    mock_v21 = MagicMock()
    mock_v21.resources.types = mock_resources_types
    mock_v21.services.types = mock_services_types
    mock_v21.services.services = mock_services_services
    mock_v21.enums.types = mock_enums_types
    mock_v21.types = mock_types_types

    # Mock the specific imports needed by ad_group tools
    mock_resources_types.ad_group = MagicMock()
    mock_services_types.ad_group_service = MagicMock()
    mock_enums_types.ad_group_status = MagicMock()
    mock_types_types.criterion = MagicMock()

    # Mock the specific imports needed by campaign tools
    mock_resources_types.campaign = MagicMock()
    mock_resources_types.campaign_budget = MagicMock()
    mock_services_types.campaign_service = MagicMock()
    mock_services_types.campaign_budget_service = MagicMock()
    mock_enums_types.campaign_status = MagicMock()
    mock_enums_types.advertising_channel_type = MagicMock()

    # Register in sys.modules
    sys.modules["google.ads.googleads.v21"] = mock_v21
    sys.modules["google.ads.googleads.v21.resources"] = mock_v21.resources
    sys.modules["google.ads.googleads.v21.resources.types"] = mock_resources_types
    sys.modules["google.ads.googleads.v21.services"] = mock_v21.services
    sys.modules["google.ads.googleads.v21.services.types"] = mock_services_types
    sys.modules["google.ads.googleads.v21.services.services"] = mock_services_services
    sys.modules["google.ads.googleads.v21.enums"] = mock_v21.enums
    sys.modules["google.ads.googleads.v21.enums.types"] = mock_enums_types
    sys.modules["google.ads.googleads.v21.types"] = mock_types_types


# Set up mocks at import time for this conftest
_setup_google_ads_mocks()
