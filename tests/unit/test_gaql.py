import pytest
from mcp_google_ads.gaql import validate_query


class TestValidateQuery:
    def test_accepts_valid_select(self):
        validate_query("SELECT campaign.id, campaign.name FROM campaign")

    def test_accepts_valid_select_limit(self):
        validate_query("SELECT campaign.id FROM campaign LIMIT 10")

    def test_rejects_select_star(self):
        with pytest.raises(ValueError, match="SELECT \\* is not allowed"):
            validate_query("SELECT * FROM campaign")

    def test_rejects_drop(self):
        with pytest.raises(ValueError, match="disallowed pattern"):
            validate_query("SELECT 1; DROP TABLE users")

    def test_rejects_delete(self):
        with pytest.raises(ValueError, match="disallowed pattern"):
            validate_query("SELECT campaign.id; DELETE FROM campaign")

    def test_rejects_insert(self):
        with pytest.raises(ValueError, match="disallowed pattern"):
            validate_query("INSERT INTO campaign VALUES (1)")

    def test_rejects_update(self):
        with pytest.raises(ValueError, match="disallowed pattern"):
            validate_query("UPDATE campaign SET name = 'x'")

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="empty"):
            validate_query("")
