# 🛠️ Installation Guide: EPO FastMCP Server

Follow these steps to connect your AI directly to the European Patent Office. This guide is designed for both developers and IPR professionals.

---

## 📋 Prerequisites

Before you start, ensure you have the following installed on your system:
*   [Python 3.12+](https://www.python.org/downloads/)
*   [uv](https://github.com/astral-sh/uv) (The fast Python package manager)
*   [Claude Desktop](https://claude.ai/download) (If you want to use it with the Claude interface)

---

## 🔑 Step 1: Get Your EPO API Credentials

The server communicates with the official **EPO Open Patent Services (OPS) v3.2 API**. 

1.  **Register:** Create a free account at the [EPO Developers Portal](https://developers.epo.org/).
2.  **Create an App:** Once logged in, go to "My Apps" and create a new application.
3.  **Get Keys:** Copy your **Consumer Key** and **Consumer Secret**. You will need these in Step 3.

---

## 📥 Step 2: Download and Setup

Clone the repository and move into the project directory:

```bash
git clone https://github.com/BrijMohan10111/epo-patent-mcp-server
cd epo-patent-mcp-server
```

---

## ⚙️ Step 3: Configure Environment Variables

Create a file named `.env` in the root of the project (you can copy `.env.example` as a starting point).

```bash
cp .env.example .env
```

Open `.env` in a text editor and fill in your keys:

```env
# Your EPO OPS API Credentials
CONSUMER_KEY=your_actual_consumer_key_here
CONSUMER_SECRET=your_actual_consumer_secret_here

# API Configuration
EPO_OPS_URL=https://ops.epo.org/3.2
```

---

## 🤖 Step 4: Integrate with Claude Desktop

To use this server within Claude, you need to tell Claude where to find it.

1.  Open your Claude Desktop Configuration file:
    *   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
    *   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
2.  Add the following entry to the `mcpServers` section:

```json
{
  "mcpServers": {
    "epo-patents": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/FULL/PATH/TO/YOUR/epo-patent-mcp-server",
        "run",
        "main.py"
      ]
    }
  }
}
```

> [!IMPORTANT]
> Replace `C:/FULL/PATH/TO/YOUR/` with the actual absolute path to the folder where you cloned the repo. Use forward slashes `/` even on Windows for the path.

---

## 🚀 Step 5: Test the Connection

1.  Restart **Claude Desktop**.
2.  Look for the 🔌 (plug icon) in the bottom right of the input box. You should see "epo-patents" listed.
3.  **Try your first prompt:**
    *   *"Who is the applicant for patent EP2933987?"*
    *   *"Run a search for autonomous driving patents published in the last 6 months."*

---

## 🛠️ Manual Testing (For Developers)

If you want to test the server logic directly without Claude, use the MCP inspector:

```bash
npx @modelcontextprotocol/inspector uv run main.py
```

---

### 🆘 Troubleshooting
*   **Authentication Errors:** Double check your `.env` for extra spaces or quotes. EPO keys take about 5-10 minutes to activate after creation.
*   **Path Issues:** Ensure the path in `claude_desktop_config.json` is absolute and points exactly to the folder containing `main.py`.
*   **Dependencies:** `uv` handles everything automatically, but ensure you have an active internet connection on the first run.
