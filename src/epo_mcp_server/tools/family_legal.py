from typing import Dict, Any
from epo_mcp_server.app import mcp, epo_client

@mcp.tool()
async def epo_ops_family(input_format: str, doc_id: str) -> Dict[str, Any]:
    """Fetch the patent family for a document."""
    endpoint = f"family/publication/{input_format}/{doc_id}"
    return await epo_client.make_request(endpoint)

@mcp.tool()
async def epo_ops_legal(input_format: str, doc_id: str) -> Dict[str, Any]:
    """Fetch the legal status for a document."""
    endpoint = f"legal/publication/{input_format}/{doc_id}"
    return await epo_client.make_request(endpoint)

@mcp.tool()
async def epo_ops_register(input_format: str, doc_id: str) -> Dict[str, Any]:
    """Fetch details from the European Patent Register."""
    endpoint = f"register/publication/{input_format}/{doc_id}"
    return await epo_client.make_request(endpoint)
