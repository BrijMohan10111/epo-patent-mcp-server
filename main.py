import sys
import os

# Add src to python path to allow imports from epo_mcp_server correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from epo_mcp_server.main import main

if __name__ == "__main__":
    main()
