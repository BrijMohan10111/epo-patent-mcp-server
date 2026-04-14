from typing import Dict, Any
from epo_mcp_server.app import mcp, epo_client
from epo_mcp_server.parsers import parse_register

@mcp.tool()
async def epo_ops_get_register_data(input_format: str, doc_id: str, include_full_history: bool = False) -> Dict[str, Any]:
    """Fetch legal/procedural data from the European Patent Register."""
    endpoint = f"register/publication/{input_format}/{doc_id}/biblio,events,procedural-steps"
    raw_data = await epo_client.make_request(endpoint)
    return parse_register(raw_data, limit=not include_full_history)
