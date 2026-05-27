"""MCP Google Ads server — FastMCP entrypoint."""

import os
import dotenv
from mcp.server.fastmcp import FastMCP

dotenv.load_dotenv()

mcp = FastMCP("google-ads")

# Import tools to register them
from mcp_google_ads.tools import read  # noqa: F401, E402
from mcp_google_ads.tools import campaign  # noqa: F401, E402
from mcp_google_ads.tools import ad_group  # noqa: F401, E402
from mcp_google_ads.tools import keyword  # noqa: F401, E402
from mcp_google_ads.tools import ad  # noqa: F401, E402


def run():
    mcp.run()


if __name__ == "__main__":
    run()