import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from epo_mcp_server.client import EPOClient

# Load configuration as early as possible
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("epo_mcp_server")

# Pre-initialize shared objects
mcp = FastMCP("EPO OPS Server")
epo_client = EPOClient()
