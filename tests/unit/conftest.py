"""Global test fixtures and mock setup for google-ads v21.

This module sets up mock v21 modules to work around the broken google-ads v21 package,
which has incomplete installation (missing services/types/ directory).
"""

import sys
import types


def _create_mock_module(name: str) -> types.ModuleType:
    """Create a mock module that can be used as a package for submodule imports."""
    module = types.ModuleType(name)
    module.__path__ = []  # Mark as package
    return module


def _setup_google_ads_mocks():
    """Set up mock v21 modules to work around broken package imports."""
    # Create the module hierarchy
    mock_v21 = _create_mock_module("google.ads.googleads.v21")

    # Create types submodules as proper modules
    mock_resources_types = _create_mock_module("google.ads.googleads.v21.resources.types")
    mock_services_types = _create_mock_module("google.ads.googleads.v21.services.types")
    mock_enums_types = _create_mock_module("google.ads.googleads.v21.enums.types")
    mock_types_types = _create_mock_module("google.ads.googleads.v21.types")
    mock_services_services = _create_mock_module("google.ads.googleads.v21.services.services")

    # Mock the specific imports needed by ad_group tools
    mock_ad_group = types.ModuleType("google.ads.googleads.v21.resources.types.ad_group")
    mock_ad_group_service = types.ModuleType("google.ads.googleads.v21.services.types.ad_group_service")
    mock_ad_group_status = types.ModuleType("google.ads.googleads.v21.enums.types.ad_group_status")
    mock_criterion = types.ModuleType("google.ads.googleads.v21.types.criterion")

    # Mock the specific imports needed by campaign tools
    mock_campaign = types.ModuleType("google.ads.googleads.v21.resources.types.campaign")
    mock_campaign_budget = types.ModuleType("google.ads.googleads.v21.resources.types.campaign_budget")
    mock_campaign_service = types.ModuleType("google.ads.googleads.v21.services.types.campaign_service")
    mock_campaign_budget_service = types.ModuleType("google.ads.googleads.v21.services.types.campaign_budget_service")
    mock_campaign_status = types.ModuleType("google.ads.googleads.v21.enums.types.campaign_status")
    mock_advertising_channel_type = types.ModuleType("google.ads.googleads.v21.enums.types.advertising_channel_type")

    # Add necessary classes to mock modules
    # AdGroup
    class AdGroup:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    # AdGroupOperation
    class AdGroupOperation:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    # AdGroupStatusEnum
    class CampaignStatus:
        class CampaignStatusEnumInner:
            def __init__(self):
                pass
            class Status:
                ENABLED = "ENABLED"
                PAUSED = "PAUSED"
                REMOVED = "REMOVED"
            Value = lambda x: x

        def __init__(self):
            self.PAUSED = "PAUSED"
            self.ENABLED = "ENABLED"
            self.REMOVED = "REMOVED"

    # Set up AdGroupStatusEnum
    mock_ad_group_status.CampaignStatusEnum = CampaignStatus()

    # Campaign
    class Campaign:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    # CampaignBudget
    class CampaignBudget:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    # CampaignOperation
    class CampaignOperation:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    # CampaignBudgetOperation
    class CampaignBudgetOperation:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    # Set up enums - use a class with proper Value method signature
    class _StatusEnum:
        """Mock status enum class that works like google ads enums."""
        ENABLED = 'ENABLED'
        PAUSED = 'PAUSED'
        REMOVED = 'REMOVED'
        SEARCH = 'SEARCH'
        DISPLAY = 'DISPLAY'
        VIDEO = 'VIDEO'
        SHOPPING = 'SHOPPING'
        PERFORMANCE_MAX = 'PERFORMANCE_MAX'

        def Value(self, name):
            return getattr(self, name, name)

    mock_ad_group_status.AdGroupStatusEnum = type('AdGroupStatusEnum', (), {
        'AdGroupStatus': _StatusEnum()
    })()

    mock_campaign_status.CampaignStatusEnum = type('CampaignStatusEnum', (), {
        'CampaignStatus': _StatusEnum()
    })()

    mock_advertising_channel_type.AdvertisingChannelTypeEnum = type('AdvertisingChannelTypeEnum', (), {
        'AdvertisingChannelType': _StatusEnum()
    })()

    # Set classes on mock modules
    mock_ad_group.AdGroup = AdGroup
    mock_ad_group_service.AdGroupOperation = AdGroupOperation
    mock_resources_types.AdGroup = AdGroup
    mock_services_types.AdGroupOperation = AdGroupOperation
    mock_campaign.Campaign = Campaign
    mock_campaign_budget.CampaignBudget = CampaignBudget
    mock_campaign_service.CampaignOperation = CampaignOperation
    mock_campaign_budget_service.CampaignBudgetOperation = CampaignBudgetOperation
    mock_resources_types.Campaign = Campaign
    mock_resources_types.CampaignBudget = CampaignBudget
    mock_services_types.CampaignOperation = CampaignOperation
    mock_services_types.CampaignBudgetOperation = CampaignBudgetOperation

    # Register in sys.modules
    sys.modules["google.ads.googleads.v21"] = mock_v21
    sys.modules["google.ads.googleads.v21.resources"] = _create_mock_module("google.ads.googleads.v21.resources")
    sys.modules["google.ads.googleads.v21.resources.types"] = mock_resources_types
    sys.modules["google.ads.googleads.v21.services"] = _create_mock_module("google.ads.googleads.v21.services")
    sys.modules["google.ads.googleads.v21.services.types"] = mock_services_types
    sys.modules["google.ads.googleads.v21.services.services"] = mock_services_services
    sys.modules["google.ads.googleads.v21.enums"] = _create_mock_module("google.ads.googleads.v21.enums")
    sys.modules["google.ads.googleads.v21.enums.types"] = mock_enums_types
    sys.modules["google.ads.googleads.v21.types"] = mock_types_types

    # Register the leaf modules too
    sys.modules["google.ads.googleads.v21.resources.types.ad_group"] = mock_ad_group
    sys.modules["google.ads.googleads.v21.services.types.ad_group_service"] = mock_ad_group_service
    sys.modules["google.ads.googleads.v21.enums.types.ad_group_status"] = mock_ad_group_status
    sys.modules["google.ads.googleads.v21.types.criterion"] = mock_criterion
    sys.modules["google.ads.googleads.v21.resources.types.campaign"] = mock_campaign
    sys.modules["google.ads.googleads.v21.resources.types.campaign_budget"] = mock_campaign_budget
    sys.modules["google.ads.googleads.v21.services.types.campaign_service"] = mock_campaign_service
    sys.modules["google.ads.googleads.v21.services.types.campaign_budget_service"] = mock_campaign_budget_service
    sys.modules["google.ads.googleads.v21.enums.types.campaign_status"] = mock_campaign_status
    sys.modules["google.ads.googleads.v21.enums.types.advertising_channel_type"] = mock_advertising_channel_type


# Set up mocks at import time for this conftest
_setup_google_ads_mocks()
