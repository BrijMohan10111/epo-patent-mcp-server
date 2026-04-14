# EPO FastMCP Server Test Suite

This document defines the manual and automated verification tests for the EPO FastMCP server.

## 🛠️ Connectivity Tests

### 1. API Authentication
*   **Prompt:** "Who is the owner of patent EP2933987?"
*   **Expected Result:** The AI should correctly identify the applicant (e.g., 'Samsung') and show that it successfully connected to the EPO OPS API.

### 2. Basic Search
*   **Prompt:** "Search for recent patents by 'Google' about 'quantum computing'."
*   **Expected Result:** A list of patents with title and identifiers returned.

## 📊 Feature Verification

### 1. Classification Search
*   **Prompt:** "What does the CPC classification code H04W36/00 mean?"
*   **Expected Result:** Correct definition from the EPO classification service.

### 2. Procedural History
*   **Prompt:** "Show me the procedural history and legal status for patent EP2933987."
*   **Expected Result:** A summary of status changes and register events.

### 3. Citations & Family
*   **Prompt:** "What are the common citations for the family of EP2933987?"
*   **Expected Result:** A list of cited patent and non-patent documents.

## 🧪 Technical Tests (Command Line)

To verify the server starts and registers all tools:

```bash
uv run main.py
```

Check the inspector:
```bash
npx @modelcontextprotocol/inspector uv run main.py
```
