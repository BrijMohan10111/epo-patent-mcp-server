import os
import json
import base64
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from mcp.server.fastmcp import FastMCP

# Load configuration
load_dotenv()
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
EPO_OPS_URL = os.getenv("EPO_OPS_URL", "https://ops.epo.org/3.2")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("epo_mcp_server")

mcp = FastMCP("EPO OPS Server")

class EPOClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.access_token = None
        self.token_expiry = None

    async def get_token(self):
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        if not CONSUMER_KEY or not CONSUMER_SECRET:
            raise ValueError("Consumer API keys for EPO OPS are not set")

        auth_str = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"grant_type": "client_credentials"}
        response = await self.client.post(
            f"{EPO_OPS_URL}/auth/accesstoken",
            headers=headers,
            data=data
        )
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data.get("access_token")
        
        expires_in = int(token_data.get("expires_in", 1200))
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
        
        logger.info("Successfully fetched new EPO OPS access token.")
        return self.access_token

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.NetworkError,))
    )
    async def make_request(self, endpoint: str, params: Optional[Dict] = None, extra_headers: Optional[Dict] = None):
        token = await self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        if extra_headers:
            headers.update(extra_headers)
            
        url = f"{EPO_OPS_URL}/rest-services/{endpoint}"
        logger.info(f"Making request to {url}")
        
        response = await self.client.get(url, headers=headers, params=params)
        
        throttle_status = response.headers.get("X-Throttling-Control", "")
        if throttle_status:
            logger.info(f"Throttling Status: {throttle_status}")
            
        if response.status_code >= 400:
            logger.error(f"Error fetching {url}: Status {response.status_code} - {response.text}")
            
        # Ignore 404s for parsing.
        if response.status_code == 404:
            return {"error": "Not Found", "message": "No results or document found for your query"}
            
        response.raise_for_status()
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"raw_text": response.text}

epo_client = EPOClient()

@mcp.tool()
async def epo_ops_search(query: str, range_start: int = 1, range_end: int = 25) -> Dict[str, Any]:
    """Search for published patents in EPO via CQL (Common Query Language).
    
    USE THIS TOOL WHEN: You need to search for patents by keywords, applicant, or classification.
    
    Args:
        query: CQL string (e.g., 'applicant=Google AND ti=neural network').
        range_start: Start index (e.g., 1).
        range_end: End index (max spread typically 100).
    """
    params = {"q": query}
    headers = {"X-OPS-Range": f"{range_start}-{range_end}"}
    return await epo_client.make_request("published-data/search", params=params, extra_headers=headers)

@mcp.tool()
async def epo_ops_published_data(doc_format: str, doc_id: str, constituent: str) -> Dict[str, Any]:
    """Get published data by format, ID, and constituent component.
    
    USE THIS TOOL WHEN: You need specific details (biblio, abstract, description, claims, fulltext, images)
    for a single document.
    
    Args:
        doc_format: Typically 'epodoc' or 'docdb' (e.g., 'epodoc').
        doc_id: The document identifier (e.g., 'EP1000000A1').
        constituent: The part to fetch. Must be one of: 'biblio', 'abstract', 'description', 'claims', 'fulltext', 'images'.
    """
    valid_constituents = {'biblio', 'abstract', 'description', 'claims', 'fulltext', 'images'}
    if constituent not in valid_constituents:
        return {"error": f"Invalid constituent. Choose from: {valid_constituents}"}
        
    endpoint = f"published-data/publication/{doc_format}/{doc_id}/{constituent}"
    return await epo_client.make_request(endpoint)

@mcp.tool()
async def epo_ops_family(doc_format: str, doc_id: str, constituent: str = "") -> Dict[str, Any]:
    """Get patent family (INPADOC extended) details or its specific components.
    
    USE THIS TOOL WHEN: You need to see related patents and continuity across different countries.
    
    Args:
        doc_format: Typically 'epodoc' (e.g., 'epodoc').
        doc_id: The document identifier (e.g., 'EP1000000A1').
        constituent: (Optional) Suffix like 'biblio' or 'legal' to get those details for the family.
    """
    endpoint = f"family/publication/{doc_format}/{doc_id}/"
    if constituent:
        endpoint += constituent
    return await epo_client.make_request(endpoint)

@mcp.tool()
async def epo_ops_legal(doc_format: str, doc_id: str) -> Dict[str, Any]:
    """Get INPADOC legal status and events.
    
    USE THIS TOOL WHEN: You need to track the legal lifecycle (grants, lapses, transfers).
    
    Args:
        doc_format: Format, e.g., 'epodoc'.
        doc_id: Document ID.
    """
    endpoint = f"legal/publication/{doc_format}/{doc_id}"
    return await epo_client.make_request(endpoint)

@mcp.tool()
async def epo_ops_register(doc_format: str, doc_id: str) -> Dict[str, Any]:
    """Get European Patent Register details.
    
    USE THIS TOOL WHEN: You need procedural data, opposition status, or unitary patent info
    for an EP application.
    
    Args:
        doc_format: Format, e.g., 'epodoc'.
        doc_id: EP Document ID (e.g., 'EP1000000A1').
    """
    endpoint = f"register/publication/{doc_format}/{doc_id}"
    return await epo_client.make_request(endpoint)

@mcp.tool()
async def epo_ops_number_service(number_type: str, input_format: str, doc_id: str, output_format: str) -> Dict[str, Any]:
    """Convert patent identifiers between docdb, epodoc, and original formats.
    
    USE THIS TOOL WHEN: You have a document ID in one format but need it in another.
    
    Args:
        number_type: Type of number (application, publication, priority).
        input_format: Format of the input ID (e.g., 'epodoc').
        doc_id: Document ID.
        output_format: Target format (e.g., 'docdb').
    """
    endpoint = f"number-service/{number_type}/{input_format}/{doc_id}/{output_format}"
    return await epo_client.make_request(endpoint)

@mcp.tool()
async def epo_get_pdf_link(country: str, doc_number: str, kind: str) -> Dict[str, str]:
    """Generate a direct link to the original PDF document on Espacenet.
    
    USE THIS TOOL WHEN: You need to download the official original patent scan.
    
    Args:
        country: Country code (e.g., 'EP', 'US').
        doc_number: Document number (e.g., '2933987').
        kind: Kind code (e.g., 'A1', 'B1').
    """
    # Standard Espacenet URL format for the original document
    espacenet_url = f"https://worldwide.espacenet.com/publicationDetails/originalDocument?CC={country}&NR={doc_number}&KC={kind}&FT=D"
    
    return {
        "espacenet_pdf_link": espacenet_url,
        "instructions": "Click the link above to view/download the original PDF document from the EPO Espacenet portal."
    }


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
    """Guide for conducting a comprehensive prior art search using EPO.

    USE THIS PROMPT WHEN: You need to find existing European patents or international
    publications relevant to an invention for patentability assessment.
    """
    return (
        "To perform a comprehensive prior art search in EPO:\\n"
        "1. Start by forming a CQL query with `epo_ops_search`. Use `ti` (title) and `abstract`\\n"
        "   or `ipc`/`cpc` classification symbols to cast a wide net.\\n"
        "2. Review the search results and identify key `doc_id` formats (e.g. EP... or WO...).\\n"
        "3. Look up the `abstract` and `claims` using `epo_ops_published_data` for relevant IDs.\\n"
        "4. If a patent looks highly relevant, use `epo_ops_family` to find translated equivalents or check its continuity.\\n"
        "5. Finally, check `epo_ops_legal` to see if the patent is still active."
    )

if __name__ == "__main__":
    mcp.run()
