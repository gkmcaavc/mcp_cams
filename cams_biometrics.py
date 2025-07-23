from typing import Any
import httpx
import json
from mcp.server.fastmcp import FastMCP

# Constants
USER_AGENT = "MyFastMCPApp/1.0 (contact@example.com)"
URL = "http://localhost:9050"

# Initialize FastMCP server
mcp = FastMCP("cams-biometrics")

async def make_nws_request(url: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Make a POST request to the API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def get_verify_serial_number(serial: str, auth_token: str) -> str:
    """Verify serial number by sending it to the API via POST.

    Args:
        serial: Serial number of the device.
        auth_token: Authorization token.
    """
    url = f"{URL}/verify_serialnumber"
    payload = {
        "serial": serial,
        "auth_token": auth_token
    }

    data = await make_nws_request(url, payload)

    if not data:
        return "Unable to fetch verify serial number call."
    
    return json.dumps(data, indent=2)

@mcp.tool()
async def get_online_status(serial: str, auth_token: str) -> str:
    """Find serial number is online or offline by sending it to the API via POST.

    Args:
        serial: Serial number of the device.
        auth_token: Authorization token.
    """
    url = f"{URL}/online_status"
    payload = {
        "serial": serial,
        "auth_token": auth_token
    }

    data = await make_nws_request(url, payload)

    if not data:
        return "Unable to fetch to find online status for your biometrics machine."
    
    return json.dumps(data, indent=2)

# if __name__ == "__main__":
#     mcp.run(transport='stdio')

# Add this at the bottom, replace the existing if __name__ == "__main__" block:
if __name__ == "__main__":
    import os
    # Get port from environment (Railway sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    # Run as HTTP server instead of stdio
    mcp.run(transport='http', port=port, host='0.0.0.0')