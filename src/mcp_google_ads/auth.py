"""Environment validation and customer ID normalization."""

import os
import re
from dataclasses import dataclass

import dotenv

dotenv.load_dotenv()

CUSTOMER_ID_RE = re.compile(r"^\d{10}$")


class ValidationError(Exception):
    pass


@dataclass
class EnvConfig:
    developer_token: str
    client_id: str
    client_secret: str
    refresh_token: str
    login_customer_id: str | None


def validate_env() -> EnvConfig:
    missing = []
    developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "").strip()
    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "").strip()
    refresh_token = os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "").strip()
    login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip() or None

    if not developer_token:
        missing.append("GOOGLE_ADS_DEVELOPER_TOKEN")
    if not client_id:
        missing.append("GOOGLE_ADS_CLIENT_ID")
    if not client_secret:
        missing.append("GOOGLE_ADS_CLIENT_SECRET")
    if not refresh_token:
        missing.append("GOOGLE_ADS_REFRESH_TOKEN")

    if missing:
        raise ValidationError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in the values."
        )

    return EnvConfig(
        developer_token=developer_token,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        login_customer_id=login_customer_id,
    )


def normalize_customer_id(customer_id: str) -> str:
    """Strip dashes and spaces; verify 10 digits. Raises ValidationError on bad format."""
    digits_only = customer_id.strip().replace("-", "").replace(" ", "")
    if not CUSTOMER_ID_RE.match(digits_only):
        raise ValidationError(
            f"Invalid customer ID: '{customer_id}'. Must be exactly 10 digits, "
            "optionally with dashes or spaces. Got: '{digits_only}'"
        )
    return digits_only