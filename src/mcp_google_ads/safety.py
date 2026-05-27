"""Safety wrappers: _execute(), execute_mutate(), audit logging."""

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any, Callable, TypeVar

from google.ads.googleads.errors import GoogleAdsException

from mcp_google_ads.errors import ToolError

T = TypeVar("T")

logger = logging.getLogger(__name__)

AUDIT_DIR = Path.home() / ".mcp_google_ads"
AUDIT_DIR.mkdir(exist_ok=True)
AUDIT_LOG_PATH = AUDIT_DIR / "audit.log"


def _get_error_code_name(ex: GoogleAdsException) -> str:
    """Extract the error code name string from a GoogleAdsException."""
    try:
        for error in ex.failure.errors:
            which_oneof = error.error_code.WhichOneof("error_code")
            if which_oneof:
                return which_oneof
            enum_name = error.error_code.__class__.__name__
            return enum_name
    except Exception:
        pass
    return "UNKNOWN_ERROR"


def _execute(callable_fn: Callable[[], T]) -> T:
    """Execute a Google Ads API call. Maps GoogleAdsException to ToolError."""
    try:
        return callable_fn()
    except GoogleAdsException as ex:
        error_code = _get_error_code_name(ex)
        errors = []
        for err in ex.failure.errors:
            field = None
            if err.location and err.location.field_path_elements:
                field = ".".join(f.name for f in err.location.field_path_elements)
            errors.append({
                "code": error_code,
                "message": err.message,
                "field": field,
            })
        hint = None
        from mcp_google_ads.errors import HINTS
        hint = HINTS.get(error_code)
        raise ToolError(
            error_code=error_code,
            message=f"Google Ads API error (request_id={ex.request_id})",
            hint=hint,
        ) from ex


def execute_mutate(
    callable_fn: Callable[[], Any],
    tool_name: str,
    customer_id: str,
    args: dict,
    dry_run: bool,
) -> dict:
    """Execute a mutate operation with audit logging. Returns result dict."""
    audit_logger = AuditLogger(AUDIT_LOG_PATH)

    def do_call():
        return callable_fn()

    result = _execute(do_call)
    result_dict = _mutate_result_to_dict(result)
    result_dict["dry_run"] = dry_run

    audit_logger.log(
        tool=tool_name,
        customer_id=customer_id,
        args=args,
        dry_run=dry_run,
        result="ok",
        resource_names=result_dict.get("resource_names", []),
    )

    return result_dict


def _mutate_result_to_dict(result: Any) -> dict:
    """Convert a mutate response proto to a plain dict."""
    if result is None:
        return {"validated": True, "applied": False, "resource_names": [], "would_change": []}
    try:
        resource_names = [m.resource_name for m in result.results]
        return {
            "validated": True,
            "applied": True,
            "resource_names": resource_names,
            "would_change": [],
        }
    except Exception:
        return {"validated": True, "applied": True, "resource_names": [], "would_change": []}


class AuditLogger:
    """Appends JSON one-liners to the audit log file."""

    def __init__(self, path: Path = AUDIT_LOG_PATH):
        self.path = path

    def log(
        self,
        tool: str,
        customer_id: str,
        args: dict,
        dry_run: bool,
        result: str,
        resource_names: list[str],
        error: str | None = None,
    ) -> None:
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "uuid": str(uuid.uuid4()),
            "tool": tool,
            "customer_id": customer_id,
            "args": args,
            "dry_run": dry_run,
            "result": result,
            "resource_names": resource_names,
        }
        if error:
            entry["error"] = error
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
