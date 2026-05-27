"""Keyword mutate tools."""

from typing import Any, Literal

from mcp.server.fastmcp import Context

from mcp_google_ads.auth import normalize_customer_id
from mcp_google_ads.client import get_client
from mcp_google_ads.safety import execute_mutate
from mcp_google_ads.server import mcp


def _ad_group_resource_name(customer_id: str, ad_group_id: str) -> str:
    return f"customers/{customer_id}/adGroups/{ad_group_id}"


@mcp.tool()
def add_keywords(
    customer_id: str,
    ad_group_id: str,
    keywords: list[dict[str, Any]],
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict:
    """Add keywords to an ad group.

    Args:
        keywords: List of keyword dicts, each with:
            - text: keyword text (e.g. "shoes")
            - match_type: "EXACT", "PHRASE", or "BROAD"
            - cpc_bid_micros: optional CPC bid in micros
    """
    from google.ads.googleads.v18.resources.types.criterion import Keyword
    from google.ads.googleads.v18.services.types.ad_group_criterion_service import AdGroupCriterionOperation
    from google.ads.googleads.v18.enums.types.keyword_match_type import KeywordMatchTypeEnum

    cid = normalize_customer_id(customer_id)
    client = get_client()
    service = client.get_service("AdGroupCriterionService")

    operations = []
    for kw in keywords:
        text = kw.get("text", "")
        match_type_str = kw.get("match_type", "EXACT").upper()
        match_type = KeywordMatchTypeEnum.KeywordMatchType.Value(match_type_str)

        keyword_info = Keyword(text=text, match_type=match_type)

        criterion = keyword_info
        if "cpc_bid_micros" in kw:
            from google.ads.googleads.v18.types.criterion import CpcBidMicros
            criterion = Keyword(text=text, match_type=match_type, cpc_bid_micros=kw["cpc_bid_micros"])

        operation = AdGroupCriterionOperation(
            create=criterion,
        )
        operations.append(operation)

    def do_mutate():
        return service.mutate_ad_group_criteria(
            customer_id=cid,
            operations=operations,
            validate_only=dry_run,
        )

    return execute_mutate(
        do_mutate,
        tool_name="add_keywords",
        customer_id=cid,
        args={"ad_group_id": ad_group_id, "keywords": keywords},
        dry_run=dry_run,
    )


@mcp.tool()
def set_keyword_status(
    customer_id: str,
    criterion_resource_name: str,
    status: Literal["ENABLED", "PAUSED", "REMOVED"],
    dry_run: bool = True,
    ctx: Context | None = None,
) -> dict:
    """Pause, enable, or remove a keyword.

    Args:
        criterion_resource_name: The full resource name, e.g. "customers/123/adGroupCriteria/456~789"
    """
    from google.ads.googleads.v18.resources.types.ad_group_criterion import AdGroupCriterion
    from google.ads.googleads.v18.services.types.ad_group_criterion_service import AdGroupCriterionOperation
    from google.ads.googleads.v18.enums.types.keyword_status import KeywordStatusEnum
    from google.protobuf.field_mask_pb2 import FieldMask

    cid = normalize_customer_id(customer_id)
    client = get_client()
    service = client.get_service("AdGroupCriterionService")

    status_value = KeywordStatusEnum.KeywordStatus.Value(status.upper())

    criterion = AdGroupCriterion(
        resource_name=criterion_resource_name,
        status=status_value,
    )

    operation = AdGroupCriterionOperation(
        update=criterion,
        update_mask=FieldMask(paths=["status"]),
    )

    def do_mutate():
        return service.mutate_ad_group_criteria(
            customer_id=cid,
            operations=[operation],
            validate_only=dry_run,
        )

    return execute_mutate(
        do_mutate,
        tool_name="set_keyword_status",
        customer_id=cid,
        args={"criterion_resource_name": criterion_resource_name, "status": status},
        dry_run=dry_run,
    )