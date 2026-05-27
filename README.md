# MCP Google Ads

An MCP (Model Context Protocol) server that lets Claude read and manage Google Ads campaigns through the Google Ads API.

## Features

- **Read tools**: Query campaign data, list campaigns, get performance metrics
- **Write tools**: Create/update/pause campaigns, ad groups, keywords, and ads
- **Safety first**: All write operations default to dry-run mode (`validate_only=True`)
- **Audit logging**: Every mutation is logged to `~/.mcp_google_ads/audit.log`

## Account Setup

This project uses 3 Google accounts with distinct roles:

| Account | Role | What you need |
|---------|------|---------------|
| **Mail A** | Developer Token | Developer token from an MCC account |
| **Mail B** | Target Ads Account | The account containing your campaigns |
| **Mail C** | OAuth Client | GCP project with OAuth 2.0 credentials |

### Prerequisites

1. **Google Ads Developer Token** (Mail A)
   - Apply at: https://ads.google.com → Tools → Settings → API Center
   - Set as `GOOGLE_ADS_DEVELOPER_TOKEN` in `.env`

2. **OAuth 2.0 Client** (Mail C)
   - Create at: https://console.cloud.google.com → APIs & Services → Credentials
   - Create OAuth 2.0 Client ID (Desktop app type)
   - Set `GOOGLE_ADS_CLIENT_ID` and `GOOGLE_ADS_CLIENT_SECRET` in `.env`

3. **Direct Access to Ads Account** (Mail B or a user with access)
   - The OAuth user must have direct access to account B
   - Account B does NOT need to be linked to Mail A's MCC

## Installation

```bash
# Clone and install dependencies
cd mcp-google-ads
pip install -e ".[dev]"

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials

# Generate refresh token (one-time)
python scripts/generate_refresh_token.py
# Follow the browser prompts and log in with the account that has access to your Ads account

# Verify setup
python scripts/smoke_test.py
```

## Configuration

Create a `.env` file:

```env
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_from_mail_A
GOOGLE_ADS_CLIENT_ID=your_oauth_client_id_from_mail_C
GOOGLE_ADS_CLIENT_SECRET=your_oauth_client_secret_from_mail_C
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token_from_generate_refresh_token_script
```

## Tools

### Read Tools

| Tool | Description |
|------|-------------|
| `search_ads` | Execute raw GAQL queries |
| `list_accessible_customers` | List all accounts your credentials can access |
| `list_campaigns` | List campaigns with status and budget |
| `get_campaign_performance` | Get impressions, clicks, cost, conversions |

### Campaign Tools

| Tool | Description |
|------|-------------|
| `set_campaign_status` | Pause, enable, or remove a campaign |
| `set_campaign_budget` | Update campaign budget |
| `create_campaign` | Create a new campaign |
| `update_campaign` | Update campaign fields (name, dates) |

### Ad Group Tools

| Tool | Description |
|------|-------------|
| `set_ad_group_status` | Pause, enable, or remove an ad group |
| `create_ad_group` | Create an ad group |
| `update_ad_group` | Update ad group fields |

### Keyword Tools

| Tool | Description |
|------|-------------|
| `add_keywords` | Add keywords to an ad group |
| `set_keyword_status` | Pause, enable, or remove a keyword |

### Ad Tools

| Tool | Description |
|------|-------------|
| `create_responsive_search_ad` | Create a responsive search ad |
| `set_ad_status` | Pause, enable, or remove an ad |

## Safety Features

### Dry-Run Mode

All write tools default to `dry_run=True`, which means they validate the request without applying changes. To actually make changes:

```python
# Test first (validates only)
result = set_campaign_status("1234567890", "campaign123", "PAUSED", dry_run=True)

# Apply (when ready)
result = set_campaign_status("1234567890", "campaign123", "PAUSED", dry_run=False)
```

### Audit Log

Every mutation is logged to `~/.mcp_google_ads/audit.log`:

```json
{"ts": "2026-05-27T10:30:00Z", "tool": "set_campaign_budget", "customer_id": "1234567890", "args": {"amount_micros": 50000000}, "dry_run": false, "result": "ok"}
```

**Note**: Google Ads API does not support transactions across multiple mutate operations. There is no automatic rollback. Check the audit log if you need to manually reverse changes.

## Error Handling

| Error Code | Cause | Solution |
|------------|-------|----------|
| `AUTHENTICATION_ERROR` | Refresh token expired | Re-run `python scripts/generate_refresh_token.py` |
| `AUTHORIZATION_ERROR` | No access to account | Verify OAuth user has direct access to account B |
| `USER_PERMISSION_DENIED` | Wrong login-customer-id | Leave `GOOGLE_ADS_LOGIN_CUSTOMER_ID` unset |
| `QUOTA_ERROR` | Rate limit | Request will be retried automatically |
| `INVALID_CUSTOMER_ID` | Bad format | Use 10 digits without dashes |

## Claude Desktop Integration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "python",
      "args": ["-m", "mcp_google_ads.server"],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "...",
        "GOOGLE_ADS_CLIENT_ID": "...",
        "GOOGLE_ADS_CLIENT_SECRET": "...",
        "GOOGLE_ADS_REFRESH_TOKEN": "..."
      }
    }
  }
}
```

Or use the project from its directory:

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_google_ads.server"]
    }
  }
}
```

## Development

```bash
# Run tests
pytest tests/unit/ -v

# Run with coverage
pytest --cov=mcp_google_ads tests/unit/

# Lint
ruff check src/

# Type check
mypy src/
```

## License

MIT