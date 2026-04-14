from typing import Dict, Any
from epo_mcp_server.app import mcp, epo_client
from epo_mcp_server.parsers import get_ns_key, get_text

@mcp.tool()
async def epo_ops_get_classification_details(scheme: str, symbol: str) -> Dict[str, Any]:
    """Fetch definitions for a classification symbol."""
    endpoint = f"classification/{scheme}/{symbol}/"
    return await epo_client.make_request(endpoint)

@mcp.tool()
async def epo_ops_search_classification(scheme: str, query: str) -> Dict[str, Any]:
    """Search for relevant classification symbols."""
    endpoint = f"classification/{scheme}/search/"
    headers = {"X-OPS-Range": "1-10"}
    raw_data = await epo_client.make_request(endpoint, params={"q": query}, extra_headers=headers)
    try:
        w_p_data = get_ns_key(raw_data, "world-patent-data") or {}
        class_search = get_ns_key(w_p_data, "classification-search") or {}
        nodes_container = get_ns_key(class_search, "classification-nodes") or {}
        nodes = get_ns_key(nodes_container, "classification-node") or []
        if isinstance(nodes, dict): nodes = [nodes]
        results = []
        for node in nodes:
            symbol_node = get_ns_key(node, "classification-symbol")
            title_node = get_ns_key(node, "class-title")
            results.append({"symbol": get_text(symbol_node), "title": get_text(title_node)})
        return {"total_found": class_search.get("@total-result-count"), "results": results}
    except Exception:
        return raw_data
