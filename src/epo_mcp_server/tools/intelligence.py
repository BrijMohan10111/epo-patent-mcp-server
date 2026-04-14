from typing import Dict, Any, List
from epo_mcp_server.app import mcp
from epo_mcp_server.tools.published_data import epo_ops_published_data
from epo_mcp_server.tools.register import epo_ops_get_register_data
from epo_mcp_server.tools.fulltext import epo_ops_get_claims
from epo_mcp_server.parsers import parse_claim_dependencies

@mcp.tool()
async def epo_ops_get_strategic_summary(input_format: str, doc_id: str) -> Dict[str, Any]:
    """Provides a high-level strategic overview of a patent."""
    try:
        biblio_res = await epo_ops_published_data("publication", input_format, doc_id, "biblio")
        register_res = await epo_ops_get_register_data(input_format, doc_id)
        claims = await epo_ops_get_claims(input_format, doc_id)
        status = register_res.get("current_status", "Unknown")
        is_granted = "granted" in status.lower() or "B1" in doc_id.upper() or "B2" in doc_id.upper()
        applicant = "Unknown"
        if isinstance(biblio_res, list) and biblio_res: applicant = biblio_res[0].get("applicant", "Unknown")
        elif isinstance(biblio_res, dict): applicant = biblio_res.get("applicant", "Unknown")
        claim_analysis = parse_claim_dependencies(claims)
        independent_claims = [c["claim_num"] for c in claim_analysis if not c["dependencies"]]
        return {
            "doc_id": doc_id,
            "title": biblio_res[0].get("title") if isinstance(biblio_res, list) and biblio_res else "Unknown",
            "applicant": applicant,
            "legal_status": status,
            "is_granted": is_granted,
            "total_claims": len(claims),
            "independent_claims_count": len(independent_claims),
            "claim_1_preview": claims[0][:500] + "..." if claims else "N/A"
        }
    except Exception as e:
        return {"error": f"Failed: {str(e)}"}

@mcp.tool()
async def epo_ops_analyze_claim_structure(input_format: str, doc_id: str) -> Dict[str, Any]:
    """Analyzes the dependency structure of patent claims."""
    try:
        claims = await epo_ops_get_claims(input_format, doc_id)
        structured = parse_claim_dependencies(claims)
        independent = [c["claim_num"] for c in structured if not c["dependencies"]]
        dependent = [c["claim_num"] for c in structured if c["dependencies"]]
        return {"doc_id": doc_id, "total_claims": len(claims), "independent_claims": independent, "dependent_claims": dependent}
    except Exception as e:
        return {"error": f"Failed: {str(e)}"}
