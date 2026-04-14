import os
import base64
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logger = logging.getLogger("epo_mcp_server.client")

class EPOClient:
    """ASynchronous client for the European Patent Office (EPO) Open Patent Services (OPS) API."""
    
    def __init__(self, consumer_key: Optional[str] = None, consumer_secret: Optional[str] = None, base_url: str = "https://ops.epo.org/3.2"):
        self.consumer_key = consumer_key or os.getenv("CONSUMER_KEY")
        self.consumer_secret = consumer_secret or os.getenv("CONSUMER_SECRET")
        self.base_url = base_url or os.getenv("EPO_OPS_URL", "https://ops.epo.org/3.2")
        
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.access_token = None
        self.token_expiry = None

    async def get_token(self) -> str:
        """Fetches/refreshes the OAuth2 access token for EPO OPS API."""
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        if not self.consumer_key or not self.consumer_secret:
            raise ValueError("Consumer API keys (CONSUMER_KEY, CONSUMER_SECRET) for EPO OPS are not set")

        auth_str = f"{self.consumer_key}:{self.consumer_secret}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"grant_type": "client_credentials"}
        response = await self.client.post(
            f"{self.base_url}/auth/accesstoken",
            headers=headers,
            data=data
        )
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data.get("access_token")
        
        expires_in = int(token_data.get("expires_in", 0))
        # Subtracting 60 seconds as a safety buffer.
        self.token_expiry = datetime.now() + timedelta(seconds=max(0, expires_in - 60))
        
        logger.info("Successfully fetched new EPO OPS access token.")
        return self.access_token

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.NetworkError,))
    )
    async def make_request(self, endpoint: str, params: Optional[Dict] = None, extra_headers: Optional[Dict] = None, method: str = "GET", data: Optional[Any] = None) -> Dict[str, Any]:
        """Makes a request to the OPS API REST endpoint with automatic token handling."""
        token = await self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        if extra_headers:
            headers.update(extra_headers)
            
        url = f"{self.base_url}/rest-services/{endpoint}"
        logger.info(f"Making {method} request to {url}")
        
        response = await self.client.request(method, url, headers=headers, params=params, data=data)
        
        throttle_status = response.headers.get("X-Throttling-Control", "")
        if throttle_status:
            logger.info(f"Throttling Status: {throttle_status}")
            
        if response.status_code >= 400:
            logger.error(f"Error fetching {url}: Status {response.status_code} - {response.text}")
            
        if response.status_code == 404:
            return {"error": "Not Found", "message": f"No results or document found for your query: {url}"}
            
        response.raise_for_status()
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"raw_text": response.text}

    async def close(self):
        """Closes the underlying HTTP client session."""
        await self.client.aclose()
