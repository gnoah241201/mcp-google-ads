"""Structured error types for the MCP Google Ads server."""

HINTS: dict[str, str] = {
    "AUTHENTICATION_ERROR": "Re-run `python scripts/generate_refresh_token.py` to generate a new refresh token.",
    "AUTHORIZATION_ERROR": "Verify the OAuth user has direct access to the target Google Ads account.",
    "USER_PERMISSION_DENIED": "Leave GOOGLE_ADS_LOGIN_CUSTOMER_ID unset in your .env file.",
    "QUOTA_ERROR": "Rate limit hit. The request will be retried automatically with backoff.",
    "INVALID_CUSTOMER_ID": "Customer ID must be 10 digits without dashes or spaces.",
    "RESOURCE_NOT_FOUND": "The requested resource does not exist or has been deleted.",
}

ERROR_CODE_TO_HINT = HINTS  # alias for tests


class ToolError(Exception):
    """Raised when a Google Ads API call fails, with structured error info."""

    def __init__(self, error_code: str, message: str, hint: str | None = None):
        self.error_code = error_code
        self.message = message
        self.hint = hint or HINTS.get(error_code, "Check the Google Ads API documentation.")
        super().__init__(f"[{error_code}] {message}\nHint: {self.hint}")
        self._error_info = {
            "code": error_code,
            "message": message,
            "hint": self.hint,
        }

    def to_dict(self) -> dict:
        return self._error_info
