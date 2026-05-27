#!/usr/bin/env python3
"""Smoke test after initial setup. Verifies each setup step independently.

Run this after filling in your .env file to verify everything is configured correctly.

Usage:
    python scripts/smoke_test.py
"""

import os
import sys
from pathlib import Path

import dotenv

dotenv.load_dotenv()


def step(name: str, fn):
    try:
        result = fn()
        print(f"  [PASS] {name}")
        return True, result
    except Exception as e:
        print(f"  [FAIL] {name}")
        print(f"         Error: {e}")
        return False, None


def check_env_vars():
    """Verify required env vars are present."""
    required = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
    ]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        raise RuntimeError(f"Missing: {', '.join(missing)}")
    print(f"         Found all {len(required)} required variables")


def check_list_accessible_customers():
    """Verify we can call the Google Ads API."""
    from google.ads.googleads.client import GoogleAdsClient
    client = GoogleAdsClient.load_from_env()
    customer_service = client.get_service("CustomerService")
    response = customer_service.list_accessible_customers()
    names = list(response.resource_names)
    if not names:
        raise RuntimeError("No accessible customers found")
    print(f"         Found {len(names)} accessible account(s)")
    return names


def check_search():
    """Verify we can run a simple GAQL query."""
    from google.ads.googleads.client import GoogleAdsClient
    client = GoogleAdsClient.load_from_env()
    gads = client.get_service("GoogleAdsService")
    customer_service = client.get_service("CustomerService")
    response = customer_service.list_accessible_customers()
    first = list(response.resource_names)[0]
    cid = first.split("/")[-1]
    gads.search(customer_id=cid, query="SELECT customer.id FROM customer LIMIT 1")
    print(f"         Query succeeded for customer {cid}")


def main():
    print("MCP Google Ads — Smoke Test")
    print("=" * 50)
    passed = 0
    total = 0

    checks = [
        ("Environment variables set", check_env_vars),
        ("list_accessible_customers succeeds", check_list_accessible_customers),
        ("search query succeeds", check_search),
    ]

    for name, fn in checks:
        total += 1
        ok, _ = step(name, fn)
        if ok:
            passed += 1

    print("=" * 50)
    print(f"Result: {passed}/{total} passed")

    if passed == total:
        print()
        print("All checks passed! Your setup is complete.")
        print("You can now register the MCP server with Claude Desktop.")
        sys.exit(0)
    else:
        print()
        print("Some checks failed. Review errors above and fix your .env configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()