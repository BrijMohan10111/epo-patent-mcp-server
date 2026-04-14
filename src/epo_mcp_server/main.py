from epo_mcp_server.app import mcp, epo_client

# Import tool modules (this will register them)
import epo_mcp_server.tools.search
import epo_mcp_server.tools.published_data
import epo_mcp_server.tools.family_legal
import epo_mcp_server.tools.utils
import epo_mcp_server.tools.citations
import epo_mcp_server.tools.fulltext
import epo_mcp_server.tools.register
import epo_mcp_server.tools.classification
import epo_mcp_server.tools.ccd
import epo_mcp_server.tools.intelligence

@mcp.resource("epo://search-syntax")
async def resource_cql_syntax() -> str:
    """Provides a guide on CQL search syntax for EPO OPS API."""
    return (
        "Common Query Language (CQL) Examples for EPO OPS Search:\\n"
        "1. By Applicant: pa=Google OR applicant=Google\\n"
        "2. By Title: ti=neural AND ti=network\\n"
        "3. By Classification (IPC/CPC): ipc=G06N OR cpc=G06N3/08\\n"
        "4. By Inventor: in=Smith\\n"
        "5. Combined: applicant=Google AND ti=quantum\\n"
        "6. By Publication Date: pd>=20200101 AND pd<=20231231"
    )

@mcp.prompt()
async def prior_art_search_epo() -> str:
    """Guide for conducting a comprehensive prior art search using EPO."""
    return (
        "To perform a comprehensive prior art search in EPO:\\n"
        "1. Start by forming a CQL query with `epo_ops_search`. Use `ti` (title) and `abstract`\\n"
        "   or `ipc`/`cpc` classification symbols to cast a wide net.\\n"
        "2. Review the search results and identify key `doc_id` formats (e.g. EP... or WO...).\\n"
        "3. Look up the `abstract` and `claims` using `epo_ops_published_data` for relevant IDs.\\n"
        "4. If a patent looks highly relevant, use `epo_ops_family` to find translated equivalents or check its continuity.\\n"
        "5. Use `epo_ops_get_citations` to explore earlier patents it cites (backward) or newer ones citing it (forward).\\n"
        "6. Finally, check `epo_ops_legal` to see if the patent is still active."
    )

def main():
    mcp.run()

if __name__ == "__main__":
    main()
