from typing import Dict, Any
from epo_mcp_server.app import mcp, epo_client
from epo_mcp_server.parsers import clean_biblio, parse_image_links

@mcp.tool()
async def epo_ops_published_data(reference_type: str, input_format: str, doc_id: str, constituent: str = "biblio") -> Dict[str, Any]:
    """Fetch bibliographic data for a patent."""
    endpoint = f"published-data/{reference_type}/{input_format}/{doc_id}/{constituent}"
    raw_data = await epo_client.make_request(endpoint)
    if constituent == "biblio":
        return clean_biblio(raw_data)
    return raw_data

@mcp.tool()
async def epo_get_document_scans(input_format: str, doc_id: str) -> Dict[str, Any]:
    """Fetch direct links to official EPO document image scans and PDFs."""
    endpoint = f"published-data/publication/{input_format}/{doc_id}/images"
    raw_data = await epo_client.make_request(endpoint)
    links = parse_image_links(raw_data)
    if not links:
        return {"status": "error", "message": "No direct scans found."}
    return {"status": "success", "scans": links}
