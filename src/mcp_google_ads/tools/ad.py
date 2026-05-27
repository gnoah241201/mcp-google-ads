"""Ad mutate tools."""

from typing import Any, Literal

from mcp.server.fastmcp import Context

from mcp_google_ads.auth import normalize_customer_id
from mcp_google_ads.client import get_client
from mcp_google_ads.safety import execute_mutate
from mcp_google_ads.server import mcp


def _ad_group_resource_name(customer_id: str, ad_group_id: str) -> str:
    return f"customers/{customer_id}/adGroups/{ad_group_id}"


@mcp.tool()
def create_responsive_search_ad(
    customer_id: str,
    ad_group_id: str,
    headlines: list[str],
    descriptions: list[str],
    final_urls: list[str],
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict:
    """Create a responsive search ad.

    Args:
        headlines: List of 3-5 headlines (each 15-30 chars recommended).
        descriptions: List of 2-4 descriptions (each 90 chars recommended).
        final_urls: List of final URLs (at least 1 required).
    """
    from google.ads.googleads.v18.resources.types.ad_group_ad import AdGroupAd, Ad
    from google.ads.googleads.v18.services.types.ad_group_ad_service import AdGroupAdOperation
    from google.ads.googleads.v18.enums.types.ad_type import AdTypeEnum
    from google.ads.googleads.v18.enums.types.ad_group_ad_status import AdGroupAdStatusEnum

    cid = normalize_customer_id(customer_id)
    client = get_client()
    service = client.get_service("AdGroupAdService")

    # Build responsive search ad info
    from google.ads.googleads.v18.types.ad import ResponsiveSearchAdInfo

    rsa_info = ResponsiveSearchAdInfo(
        headlines=[{"text": h} for h in headlines],
        descriptions=[{"text": d} for d in descriptions],
    )

    ad = Ad(
        responsive_search_ad=rsa_info,
        final_urls=final_urls,
        type_=AdTypeEnum.AdType.RESPONSIVE_SEARCH_AD,
    )

    ad_group_ad = AdGroupAd(
        ad_group=_ad_group_resource_name(cid, ad_group_id),
        ad=ad,
        status=AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
    )

    operation = AdGroupAdOperation(create=ad_group_ad)

    def do_mutate():
        return service.mutate_ad_group_ads(
            customer_id=cid,
            operations=[operation],
            validate_only=dry_run,
        )

    return execute_mutate(
        do_mutate,
        tool_name="create_responsive_search_ad",
        customer_id=cid,
        args={
            "ad_group_id": ad_group_id,
            "headlines": headlines,
            "descriptions": descriptions,
            "final_urls": final_urls,
        },
        dry_run=dry_run,
    )


@mcp.tool()
def set_ad_status(
    customer_id: str,
    ad_id: str,
    status: Literal["ENABLED", "PAUSED", "REMOVED"],
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict:
    """Pause, enable, or remove an ad.

    Args:
        ad_id: The ad ID (numeric string).
    """
    from google.ads.googleads.v18.resources.types.ad_group_ad import AdGroupAd
    from google.ads.googleads.v18.services.types.ad_group_ad_service import AdGroupAdOperation
    from google.ads.googleads.v18.enums.types.ad_group_ad_status import AdGroupAdStatusEnum
    from google.protobuf.field_mask_pb2 import FieldMask

    cid = normalize_customer_id(customer_id)
    client = get_client()
    service = client.get_service("AdGroupAdService")

    status_value = AdGroupAdStatusEnum.AdGroupAdStatus.Value(status.upper())
    resource_name = f"customers/{cid}/adGroupAds/{ad_id}"

    ad_group_ad = AdGroupAd(
        resource_name=resource_name,
        status=status_value,
    )

    operation = AdGroupAdOperation(
        update=ad_group_ad,
        update_mask=FieldMask(paths=["status"]),
    )

    def do_mutate():
        return service.mutate_ad_group_ads(
            customer_id=cid,
            operations=[operation],
            validate_only=dry_run,
        )

    return execute_mutate(
        do_mutate,
        tool_name="set_ad_status",
        customer_id=cid,
        args={"ad_id": ad_id, "status": status},
        dry_run=dry_run,
    )
