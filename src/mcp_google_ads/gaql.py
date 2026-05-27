"""GAQL query helpers — validation and safety."""

import re

DANGEROUS_PATTERNS = [
    re.compile(r"\bDROP\b", re.IGNORECASE),
    re.compile(r"\bDELETE\b", re.IGNORECASE),
    re.compile(r"\bINSERT\b", re.IGNORECASE),
    re.compile(r"\bUPDATE\b", re.IGNORECASE),
    re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
    re.compile(r";\s*\w+", re.IGNORECASE),  # statement chaining
]


def validate_query(query: str) -> None:
    """Validate a GAQL query. Raises ValueError if unsafe or malformed."""
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    query_clean = query.strip()

    if query_clean.upper().startswith("SELECT *"):
        raise ValueError(
            "SELECT * is not allowed. List explicit fields to ensure predictable results "
            "and avoid accidentally fetching too much data."
        )

    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(query_clean):
            raise ValueError(
                f"Query contains disallowed pattern '{pattern.pattern}': {query_clean[:80]}"
            )
