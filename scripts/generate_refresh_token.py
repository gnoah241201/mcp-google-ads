#!/usr/bin/env python3
"""Generate a refresh token via OAuth 2.0 for Desktop apps.

Run once to get the refresh token, then copy it to your .env file.
This script opens a browser for the user to log in and consent.

Usage:
    1. Fill in GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET in .env
    2. Run: python scripts/generate_refresh_token.py
    3. Log in with the Google account that has access to your Ads account
    4. Copy the printed refresh token to your .env file as GOOGLE_ADS_REFRESH_TOKEN
"""

import os
import sys
from pathlib import Path

import dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/adwords"]


def main():
    # Load env from project root
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    dotenv.load_dotenv(env_path)

    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "").strip()

    if not client_id or not client_secret:
        print("Error: GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET must be set in .env first.")
        print("Copy .env.example to .env and fill in these values.")
        sys.exit(1)

    token_path = project_root / ".token.json"
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing existing token...")
            creds.refresh(Request())
        else:
            print("Starting OAuth flow...")
            print("A browser window will open. Log in with the Google account")
            print("that has access to your Google Ads account and consent to the permissions.")
            print()

            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as f:
            f.write(creds.to_json())

    print()
    print("=" * 60)
    print("OAuth flow completed successfully!")
    print("=" * 60)
    print()
    print("Your refresh token is:")
    print(creds.refresh_token)
    print()
    print("Add this to your .env file as GOOGLE_ADS_REFRESH_TOKEN")
    print()

    # Verify by listing accessible customers
    print("Verifying access...")
    os.environ["GOOGLE_ADS_REFRESH_TOKEN"] = creds.refresh_token
    os.environ["GOOGLE_ADS_CLIENT_ID"] = client_id
    os.environ["GOOGLE_ADS_CLIENT_SECRET"] = client_secret
    # Don't set developer token for verification - just list customers

    try:
        from google.ads.googleads.client import GoogleAdsClient
        client = GoogleAdsClient.load_from_env()
        customer_service = client.get_service("CustomerService")
        response = customer_service.list_accessible_customers()
        print()
        print("Accessible Google Ads accounts:")
        for rn in response.resource_names:
            print(f"  {rn}")
        print()
        print("Setup complete!")
    except Exception as e:
        print(f"Note: Could not verify (missing dev token is OK): {e}")
        print("You can now add the refresh token to .env and run smoke_test.py")


if __name__ == "__main__":
    main()