from typing import List
from epo_mcp_server.app import mcp, epo_client
from epo_mcp_server.parsers import parse_fulltext

@mcp.tool()
async def epo_ops_get_claims(input_format: str, doc_id: str, include_full_text: bool = False) -> List[str]:
    """Fetch the legal claims of a patent."""
    endpoint = f"published-data/publication/{input_format}/{doc_id}/claims"
    raw_data = await epo_client.make_request(endpoint)
    return parse_fulltext(raw_data, "claims", limit=not include_full_text)

@mcp.tool()
async def epo_ops_get_description(input_format: str, doc_id: str, include_full_text: bool = False) -> str:
    """Fetch the technical description/specification of a patent."""
    endpoint = f"published-data/publication/{input_format}/{doc_id}/description"
    raw_data = await epo_client.make_request(endpoint)
    return parse_fulltext(raw_data, "description", limit=not include_full_text)
