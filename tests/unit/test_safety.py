import pytest
import json
from unittest.mock import MagicMock, patch
from google.ads.googleads.errors import GoogleAdsException
from mcp_google_ads.safety import _execute, execute_mutate, AuditLogger


class TestExecute:
    def test_returns_result_on_success(self):
        def happy_path():
            return {"rows": [{"id": "123"}]}
        result = _execute(happy_path)
        assert result == {"rows": [{"id": "123"}]}

    def test_maps_googleads_exception_to_tool_error(self):
        from google.ads.googleads.errors import GoogleAdsException

        mock_error = MagicMock()
        mock_error.error_code.WhichOneof.return_value = "authentication_error"
        mock_error.error_code.authentication_error = 1
        mock_error.message = "Token expired"
        mock_error.location.field_path_elements = []

        mock_failure = MagicMock()
        mock_failure.errors = [mock_error]

        # Create a real GoogleAdsException with mocks
        mock_error_obj = MagicMock()
        mock_call = MagicMock()
        mock_ex = GoogleAdsException(mock_error_obj, mock_call, mock_failure, "abc123")

        from mcp_google_ads.errors import ToolError

        def raiser():
            raise mock_ex

        with pytest.raises(ToolError) as exc_info:
            _execute(raiser)
        assert exc_info.value.error_code == "authentication_error"


class TestAuditLogger:
    def test_audit_log_write(self, tmp_path):
        log_path = tmp_path / "audit.log"
        logger = AuditLogger(log_path)
        logger.log("set_campaign_budget", "1234567890", {"amount_micros": 50000000}, False, "ok", [])
        content = log_path.read_text().strip()
        assert content != ""
        entry = json.loads(content)
        assert entry["tool"] == "set_campaign_budget"
        assert entry["result"] == "ok"
        assert entry["customer_id"] == "1234567890"
        assert entry["dry_run"] is False
