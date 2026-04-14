from typing import Dict, Any, List
from epo_mcp_server.app import mcp, epo_client
from epo_mcp_server.parsers import parse_ccd

@mcp.tool()
async def epo_ops_get_ccd(input_format: str, doc_id: str, include_full_family: bool = False) -> List[Dict[str, Any]]:
    """Fetch Common Citation Document (CCD) data."""
    endpoint = f"ccd/publication/{input_format}/{doc_id}"
    raw_data = await epo_client.make_request(endpoint)
    if isinstance(raw_data, dict) and "raw_text" in raw_data:
        return [{"status": "error", "message": "CCD data not found"}]
    return parse_ccd(raw_data, limit=not include_full_family)
