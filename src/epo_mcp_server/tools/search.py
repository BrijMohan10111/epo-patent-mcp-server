from typing import Dict, Any, Optional
from datetime import datetime
from epo_mcp_server.app import mcp, epo_client
from epo_mcp_server.parsers import flatten_search_results

@mcp.tool()
async def epo_ops_search(query: str, range_start: int = 1, range_end: int = 25) -> Dict[str, Any]:
    """Search for patents via CQL (Common Query Language)."""
    params = {"q": query}
    headers = {"X-OPS-Range": f"{range_start}-{range_end}"}
    raw_data = await epo_client.make_request("published-data/search/biblio", params=params, extra_headers=headers)
    return flatten_search_results(raw_data)

@mcp.tool()
async def top_latest_patents(applicant_or_keyword: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
    """Finds the most recently published patents for a keyword or applicant."""
    current_year = datetime.now().year
    query = f"pd>={current_year}0101"
    if applicant_or_keyword:
        query += f" AND (applicant={applicant_or_keyword} OR ti={applicant_or_keyword})"
    return await epo_ops_search(query, range_start=1, range_end=min(limit, 25))
