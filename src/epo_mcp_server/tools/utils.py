from typing import Dict, Any, Optional
from epo_mcp_server.app import mcp, epo_client

@mcp.tool()
async def epo_ops_number_service(number_type: str, input_format: str, doc_id: str, output_format: str) -> Dict[str, Any]:
    """Convert patent identifiers."""
    endpoint = f"number-service/{number_type}/{input_format}/{doc_id}/{output_format}"
    return await epo_client.make_request(endpoint)

@mcp.tool()
async def epo_get_pdf_link(country: str, doc_number: str, kind: Optional[str] = None) -> Dict[str, str]:
    """Generate a link to the original document on Espacenet."""
    base_url = "https://worldwide.espacenet.com/publicationDetails/originalDocument"
    params = []
    if country: params.append(f"CC={country}")
    if doc_number: params.append(f"NR={doc_number}")
    if kind: params.append(f"KC={kind}")
    query_string = "&".join(params)
    espacenet_url = f"{base_url}?{query_string}" if query_string else base_url
    return {
        "espacenet_link": espacenet_url,
        "instructions": "Click to view original PDF on Espacenet."
    }
