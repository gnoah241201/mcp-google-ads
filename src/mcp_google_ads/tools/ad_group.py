"""Ad group mutate tools."""

from typing import Literal

from mcp.server.fastmcp import Context

from mcp_google_ads.auth import normalize_customer_id
from mcp_google_ads.client import get_client
from mcp_google_ads.safety import _execute, execute_mutate
from mcp_google_ads.server import mcp


def _ad_group_resource_name(customer_id: str, ad_group_id: str) -> str:
    return f"customers/{customer_id}/adGroups/{ad_group_id}"


def _campaign_resource_name(customer_id: str, campaign_id: str) -> str:
    return f"customers/{customer_id}/campaigns/{campaign_id}"


@mcp.tool()
def set_ad_group_status(
    customer_id: str,
    ad_group_id: str,
    status: Literal["ENABLED", "PAUSED", "REMOVED"],
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict:
    """Pause, enable, or remove an ad group."""
    from google.ads.googleads.v21.resources.types.ad_group import AdGroup
    from google.ads.googleads.v21.services.types.ad_group_service import AdGroupOperation
    from google.ads.googleads.v21.enums.types.ad_group_status import AdGroupStatusEnum
    from google.protobuf.field_mask_pb2 import FieldMask

    cid = normalize_customer_id(customer_id)
    client = get_client()
    service = client.get_service("AdGroupService")

    status_value = AdGroupStatusEnum.AdGroupStatus.Value(status.upper())

    ad_group = AdGroup(
        resource_name=_ad_group_resource_name(cid, ad_group_id),
        status=status_value,
    )

    operation = AdGroupOperation(
        update=ad_group,
        update_mask=FieldMask(paths=["status"]),
    )

    def do_mutate():
        return service.mutate_ad_groups(
            customer_id=cid,
            operations=[operation],
            validate_only=dry_run,
        )

    return execute_mutate(
        do_mutate,
        tool_name="set_ad_group_status",
        customer_id=cid,
        args={"ad_group_id": ad_group_id, "status": status},
        dry_run=dry_run,
    )


@mcp.tool()
def create_ad_group(
    customer_id: str,
    campaign_id: str,
    name: str,
    cpc_bid_micros: int | None = None,
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict:
    """Create a new ad group under a campaign.

    Args:
        name: Ad group name.
        campaign_id: The campaign ID to attach this ad group to.
        cpc_bid_micros: Optional CPC bid in micros. If not provided, inherits from campaign.
    """
    from google.ads.googleads.v21.resources.types.ad_group import AdGroup
    from google.ads.googleads.v21.services.types.ad_group_service import AdGroupOperation
    from google.ads.googleads.v21.enums.types.ad_group_status import AdGroupStatusEnum

    cid = normalize_customer_id(customer_id)
    client = get_client()
    service = client.get_service("AdGroupService")

    ad_group = AdGroup(
        name=name,
        campaign=_campaign_resource_name(cid, campaign_id),
        status=AdGroupStatusEnum.AdGroupStatus.PAUSED,
    )

    if cpc_bid_micros is not None:
        from google.ads.googleads.v21.types.criterion import CpcBidMicros
        ad_group.cpc_bid_micros = cpc_bid_micros

    operation = AdGroupOperation(create=ad_group)

    def do_mutate():
        return service.mutate_ad_groups(
            customer_id=cid,
            operations=[operation],
            validate_only=dry_run,
        )

    return execute_mutate(
        do_mutate,
        tool_name="create_ad_group",
        customer_id=cid,
        args={"campaign_id": campaign_id, "name": name, "cpc_bid_micros": cpc_bid_micros},
        dry_run=dry_run,
    )


ALLOWED_UPDATE_FIELDS = {"name", "status", "cpc_bid_micros"}


@mcp.tool()
def update_ad_group(
    customer_id: str,
    ad_group_id: str,
    fields: dict,
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict:
    """Partial update for an ad group."""
    # Validate fields before expensive imports
    unknown = set(fields.keys()) - ALLOWED_UPDATE_FIELDS
    if unknown:
        raise ValueError(f"Unknown fields: {unknown}. Allowed: {ALLOWED_UPDATE_FIELDS}")

    from google.ads.googleads.v21.resources.types.ad_group import AdGroup
    from google.ads.googleads.v21.services.types.ad_group_service import AdGroupOperation
    from google.protobuf.field_mask_pb2 import FieldMask

    cid = normalize_customer_id(customer_id)
    client = get_client()
    service = client.get_service("AdGroupService")

    paths = list(fields.keys())
    update_mask = FieldMask(paths=paths)

    ad_group = AdGroup(resource_name=_ad_group_resource_name(cid, ad_group_id))
    for key, value in fields.items():
        setattr(ad_group, key, value)

    operation = AdGroupOperation(update=ad_group, update_mask=update_mask)

    def do_mutate():
        return service.mutate_ad_groups(
            customer_id=cid,
            operations=[operation],
            validate_only=dry_run,
        )

    return execute_mutate(
        do_mutate,
        tool_name="update_ad_group",
        customer_id=cid,
        args={"ad_group_id": ad_group_id, "fields": fields},
        dry_run=dry_run,
    )
