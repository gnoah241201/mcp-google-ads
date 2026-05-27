"""Campaign mutate tools."""

from typing import Literal

from mcp.server.fastmcp import Context

from mcp_google_ads.auth import normalize_customer_id
from mcp_google_ads.client import get_client
from mcp_google_ads.safety import _execute, execute_mutate
from mcp_google_ads.server import mcp


def _campaign_resource_name(customer_id: str, campaign_id: str) -> str:
    return f"customers/{customer_id}/campaigns/{campaign_id}"


@mcp.tool()
def set_campaign_status(
    customer_id: str,
    campaign_id: str,
    status: Literal["ENABLED", "PAUSED", "REMOVED"],
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict:
    """Pause, enable, or remove a campaign."""
    from google.ads.googleads.v21.enums.types.campaign_status import CampaignStatusEnum
    from google.ads.googleads.v21.resources.types.campaign import Campaign
    from google.ads.googleads.v21.services.types.campaign_service import CampaignOperation
    from google.protobuf.field_mask_pb2 import FieldMask

    cid = normalize_customer_id(customer_id)
    client = get_client()
    service = client.get_service("CampaignService")

    status_value = CampaignStatusEnum.CampaignStatus.Value(status.upper())

    campaign = Campaign(
        resource_name=_campaign_resource_name(cid, campaign_id),
        status=status_value,
    )

    operation = CampaignOperation(
        update=campaign,
        update_mask=FieldMask(paths=["status"]),
    )

    def do_mutate():
        return service.mutate_campaigns(
            customer_id=cid,
            operations=[operation],
            validate_only=dry_run,
        )

    return execute_mutate(
        do_mutate,
        tool_name="set_campaign_status",
        customer_id=cid,
        args={"campaign_id": campaign_id, "status": status},
        dry_run=dry_run,
    )


@mcp.tool()
def set_campaign_budget(
    customer_id: str,
    campaign_id: str,
    amount_micros: int,
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict:
    """Update the amount of a campaign's budget.

    Args:
        amount_micros: Budget in micros (1,000,000 = 1 unit of currency).
    """
    from google.ads.googleads.v24.resources.types.campaign_budget import CampaignBudget
    from google.ads.googleads.v24.services.types.campaign_budget_service import CampaignBudgetOperation
    from google.protobuf.field_mask_pb2 import FieldMask

    cid = normalize_customer_id(customer_id)
    client = get_client()
    gads_service = client.get_service("GoogleAdsService")

    # First get the campaign to find its budget resource name
    campaign_query = f'SELECT campaign.id, campaign.campaign_budget FROM campaign WHERE campaign.id = "{campaign_id}"'

    def get_budget():
        return gads_service.search(customer_id=cid, query=campaign_query)

    response = _execute(get_budget)
    row = next(iter(response))
    budget_resource_name = row.campaign.campaign_budget

    budget_service = client.get_service("CampaignBudgetService")

    budget = CampaignBudget(
        resource_name=budget_resource_name,
        amount_micros=str(amount_micros),
    )

    operation = CampaignBudgetOperation(
        update=budget,
        update_mask=FieldMask(paths=["amount_micros"]),
    )

    def do_mutate():
        return budget_service.mutate_campaign_budgets(
            customer_id=cid,
            operations=[operation],
        )

    return execute_mutate(
        do_mutate,
        tool_name="set_campaign_budget",
        customer_id=cid,
        args={"campaign_id": campaign_id, "amount_micros": amount_micros},
        dry_run=dry_run,
    )


@mcp.tool()
def create_campaign(
    customer_id: str,
    name: str,
    budget_micros: int,
    advertising_channel_type: Literal["SEARCH", "DISPLAY", "SHOPPING", "VIDEO", "PERFORMANCE_MAX", "UNKNOWN"] = "SEARCH",
    status: Literal["ENABLED", "PAUSED"] = "PAUSED",
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict:
    """Create a new campaign. Always creates in PAUSED status by default for safety."""
    from google.ads.googleads.v21.enums.types.advertising_channel_type import AdvertisingChannelTypeEnum
    from google.ads.googleads.v21.enums.types.campaign_status import CampaignStatusEnum
    from google.ads.googleads.v21.resources.types.campaign import Campaign
    from google.ads.googleads.v21.services.types.campaign_service import CampaignOperation

    cid = normalize_customer_id(customer_id)
    client = get_client()
    service = client.get_service("CampaignService")

    channel_enum = AdvertisingChannelTypeEnum.AdvertisingChannelType.Value(advertising_channel_type.upper())
    status_enum = CampaignStatusEnum.CampaignStatus.Value(status.upper())

    campaign = Campaign(
        name=name,
        advertising_channel_type=channel_enum,
        status=status_enum,
    )

    operation = CampaignOperation(create=campaign)

    def do_mutate():
        return service.mutate_campaigns(
            customer_id=cid,
            operations=[operation],
            validate_only=dry_run,
        )

    return execute_mutate(
        do_mutate,
        tool_name="create_campaign",
        customer_id=cid,
        args={"name": name, "budget_micros": budget_micros, "advertising_channel_type": advertising_channel_type},
        dry_run=dry_run,
    )


ALLOWED_UPDATE_FIELDS = {"name", "start_date", "end_date"}


@mcp.tool()
def update_campaign(
    customer_id: str,
    campaign_id: str,
    fields: dict,
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict:
    """Partial update for a campaign. Pass field name and new value in fields dict."""
    # Validate fields before expensive imports
    unknown = set(fields.keys()) - ALLOWED_UPDATE_FIELDS
    if unknown:
        raise ValueError(f"Unknown fields: {unknown}. Allowed: {ALLOWED_UPDATE_FIELDS}")

    from google.ads.googleads.v21.resources.types.campaign import Campaign
    from google.ads.googleads.v21.services.types.campaign_service import CampaignOperation
    from google.protobuf.field_mask_pb2 import FieldMask

    cid = normalize_customer_id(customer_id)
    client = get_client()
    service = client.get_service("CampaignService")

    paths = list(fields.keys())
    update_mask = FieldMask(paths=paths)

    campaign = Campaign(resource_name=_campaign_resource_name(cid, campaign_id))
    for key, value in fields.items():
        setattr(campaign, key, value)

    operation = CampaignOperation(update=campaign, update_mask=update_mask)

    def do_mutate():
        return service.mutate_campaigns(
            customer_id=cid,
            operations=[operation],
            validate_only=dry_run,
        )

    return execute_mutate(
        do_mutate,
        tool_name="update_campaign",
        customer_id=cid,
        args={"campaign_id": campaign_id, "fields": fields},
        dry_run=dry_run,
    )
