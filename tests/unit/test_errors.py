import pytest
from mcp_google_ads.errors import ToolError, HINTS, ERROR_CODE_TO_HINT


class TestToolError:
    def test_construct_with_code(self):
        err = ToolError("AUTHENTICATION_ERROR", "Token expired", "scripts/generate_refresh_token.py")
        assert err.error_code == "AUTHENTICATION_ERROR"
        assert "scripts/generate_refresh_token.py" in str(err)
        assert err.hint == "scripts/generate_refresh_token.py"

    def test_hints_cover_all_defined_codes(self):
        for code in ERROR_CODE_TO_HINT:
            assert code in HINTS

    def test_to_dict(self):
        err = ToolError("QUOTA_ERROR", "Rate exceeded")
        d = err.to_dict()
        assert d["code"] == "QUOTA_ERROR"
        assert d["message"] == "Rate exceeded"
        assert "hint" in d
