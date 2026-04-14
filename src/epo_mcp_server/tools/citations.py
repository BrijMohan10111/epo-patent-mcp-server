from typing import Dict, Any, List
from epo_mcp_server.app import mcp, epo_client
from epo_mcp_server.parsers import parse_citations

@mcp.tool()
async def epo_ops_get_citations(reference_type: str, input_format: str, doc_id: str) -> List[Dict[str, Any]]:
    """Fetch backward and forward citations."""
    endpoint = f"published-data/{reference_type}/{input_format}/{doc_id}/biblio"
    raw_data = await epo_client.make_request(endpoint)
    return parse_citations(raw_data)
