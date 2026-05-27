"""Read-only tools: search_ads, list_accessible_customers, list_campaigns, get_campaign_performance."""

from typing import Any

from mcp.server.fastmcp import Context

from mcp_google_ads.auth import normalize_customer_id
from mcp_google_ads.client import get_client
from mcp_google_ads.gaql import validate_query
from mcp_google_ads.safety import _execute

# Import mcp from server — must happen after server creates it
import mcp_google_ads.server as _server
mcp = _server.mcp


@mcp.tool()
def search_ads(customer_id: str, query: str, ctx: Context | None = None) -> list[dict[str, Any]]:
    """Execute a raw GAQL query against Google Ads.

    Args:
        customer_id: The 10-digit customer ID (dashes/spaces optional).
        query: A valid GAQL SELECT statement.
    """
    cid = normalize_customer_id(customer_id)
    validate_query(query)
    client = get_client()
    gads_service = client.get_service("GoogleAdsService")

    def do_search():
        return gads_service.search(customer_id=cid, query=query)

    response = _execute(do_search)
    rows = []
    for row in response:
        row_dict = {}
        # Use field access via proto reflection
        for descriptor in row.DESCRIPTOR.fields:
            value = getattr(row, descriptor.name, None)
            if value is not None and not callable(value):
                try:
                    row_dict[descriptor.name] = str(value)
                except Exception:
                    row_dict[descriptor.name] = repr(value)
        rows.append(row_dict)
    return rows


@mcp.tool()
def list_accessible_customers(ctx: Context | None = None) -> list[dict[str, str]]:
    """List all Google Ads accounts the current OAuth user can access."""
    client = get_client()
    customer_service = client.get_service("CustomerService")

    def do_list():
        return customer_service.list_accessible_customers()

    response = _execute(do_list)
    customers = []
    for resource_name in response.resource_names:
        parts = resource_name.split("/")
        acc_id = parts[-1] if parts else resource_name
        customers.append({
            "resource_name": resource_name,
            "customer_id": acc_id,
        })
    return customers


@mcp.tool()
def list_campaigns(customer_id: str, ctx: Context | None = None) -> list[dict[str, Any]]:
    """List all campaigns for a customer with status and budget."""
    cid = normalize_customer_id(customer_id)
    query = "SELECT campaign.id, campaign.name, campaign.status, campaign.budget.amount_micros FROM campaign"
    client = get_client()
    gads_service = client.get_service("GoogleAdsService")

    def do_search():
        return gads_service.search(customer_id=cid, query=query)

    response = _execute(do_search)
    campaigns = []
    for row in response:
        campaigns.append({
            "id": row.campaign.id,
            "name": row.campaign.name,
            "status": row.campaign.status.name,
            "budget_micros": int(row.campaign.budget.amount_micros),
        })
    return campaigns


@mcp.tool()
def get_campaign_performance(
    customer_id: str,
    date_range: str = "LAST_30_DAYS",
    campaign_ids: list[str] | None = None,
    ctx: Context | None = None,
) -> list[dict[str, Any]]:
    """Get impressions, clicks, cost, and conversions for campaigns.

    Args:
        customer_id: The 10-digit customer ID.
        date_range: One of LAST_7_DAYS, LAST_30_DAYS, LAST_90_DAYS, CUSTOMER_DATE_RANGE.
        campaign_ids: Optional list of campaign IDs to filter.
    """
    cid = normalize_customer_id(customer_id)

    where_clause = ""
    if campaign_ids:
        ids_str = ", ".join(f'"{c}"' for c in campaign_ids)
        where_clause = f" WHERE campaign.id IN ({ids_str})"

    query = (
        "SELECT campaign.id, campaign.name, "
        "metrics.impressions, metrics.clicks, metrics.cost_micros, "
        "metrics.conversions "
        f"FROM campaign{where_clause}"
    )

    client = get_client()
    gads_service = client.get_service("GoogleAdsService")

    def do_search():
        return gads_service.search(customer_id=cid, query=query)

    response = _execute(do_search)
    metrics = []
    for row in response:
        metrics.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "impressions": int(row.metrics.impressions),
            "clicks": int(row.metrics.clicks),
            "cost_micros": int(row.metrics.cost_micros),
            "conversions": float(row.metrics.conversions),
            "date_range": date_range,
        })
    return metrics