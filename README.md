# EPO OPS FastMCP Server

A FastMCP server built for querying the European Patent Office (EPO) Open Patent Services (OPS) v3.2 API. This connects AI models (like Claude) with comprehensive European and worldwide patent data.

## Features
- **Published Data**: Retrieve bibliographic data, abstracts, descriptions, claims, and full-text translations.
- **Search (CQL)**: Formulate and perform robust Common Query Language (CQL) queries across EPO data.
- **Family**: Obtain the INPADOC extended patent family data for any application.
- **Legal Status**: Track INPADOC legal statuses and lifecycle events.
- **Register**: Find details on opposition, procedures, and unified patent data in the Europe registers.
- **Number Service**: Convert docdb, epodoc, and other numbering formats seamlessly.
- **PDF Downloader**: Generate direct-download URLs for the original PDF scans via the Espacenet portal.

## 🚀 Installation & Setup

For a detailed step-by-step guide on how to get your EPO keys and connect this server to Claude Desktop, please see our:

👉 **[INSTALLATION.md](./INSTALLATION.md)**

### Quick Start
1. Ensure `uv` is installed.
2. Setup `.env` with `CONSUMER_KEY` and `CONSUMER_SECRET`.
3. Run: `uv run main.py`

## Adding to Claude Desktop
Add it to your Claude Desktop config (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "epo_patents": {
      "command": "uv",
      "args": [
        "--directory",
        "d:/Projects 2025/EPO Fastmcp Server/epo_mcp_server",
        "run",
        "main.py"
      ]
    }
  }
}
```

## Usage
Inside Claude, prompt for:
- "Run an EPO prior art search for..."
- "Get the claims of EP1000000A1"
- "What is the legal status for US2020123456A1?"


# 🚀 How to Talk to Your Patent Assistant: A Simple Guide

This server connects your AI directly to the European Patent Office. You don't need to be a computer expert or a lawyer to get amazing results. This guide shows exactly what questions to ask to get the answers you need.

---

## 1. Finding Patents (The "Search")
If you want to find patents about a topic or owned by a company, just ask the AI:

*   **"Find me patents owned by 'Samsung' that mention 'foldable screens'."**
*   **"What are the most recent patents about 'recycling plastic'?"**
*   **"I'm looking for patents in the 'H04W' category (Wireless communication)."**

*💡 Tip: If you are looking for a company, use the term "Applicant."*

---

## 2. Getting the Basics (The "Fact-Sheet")
Once you have a patent number (like **EP2933987**), you can ask simple questions:

*   **"Who is the owner (Applicant) of patent EP2933987?"**
*   **"Give me a simple summary (Abstract) of what this patent is about."**
*   **"Who invented this?"**
*   **"When was this patent published?"**

---

## 3. Reading the Fine Print (The "Internal View")
If you need to know exactly how an invention works or what it legally protects, ask:

*   **"Show me the full text of the 'Claims' for this patent."** (This shows the legal boundaries).
*   **"Can you give me the 'Description' of how the technology works?"** (This is the technical manual).
*   **"Give me the link to download the original PDF document."** (This gives you the official paperwork).

---

## 4. The Expert "Intelligence" Reports (The "Expert View")
We have built "Smart Tools" that do the hard work for you. Try asking these:

*   **"Give me a Strategic Summary for patent EP2933987."**
    *   *Result:* You get a one-page report showing the title, current legal status, and if it's broad or narrow.
*   **"Analyze the Claim Structure for this patent."**
    *   *Result:* The AI will tell you which claims are the "big ideas" and which ones are just small details.
*   **"Show me the 'Claim Tree' or dependencies."**
    *   *Result:* You see how the legal points connect to one another.

---

## 5. Checking the Life Cycle (The "Legal Status")
Is the patent still active? Is it expired? Ask:

*   **"Is patent EP2933987 still alive (Active)?"**
*   **"Show me the 'Register Data' for this patent."**
    *   *Result:* You see if they paid their bills, if they sold the patent, or if a competitor is fighting them in court.
*   **"Are there any 'Oppositions' filed against this patent?"** (This tells you if people are trying to cancel it).

---

## 6. The Big Picture (The "Landscape")
To see how this patent connects to the rest of the world, ask:

*   **"Show me the 'Family' of this patent."**
    *   *Result:* You see all related patents in the USA, China, Japan, etc.
*   **"What previous inventions (Citations) did the office find when checking this?"**
*   **"Give me the 'Common Citation Document' (CCD) report."**
    *   *Result:* A master list of every secret document found by EVERY patent office in the world for this family.

---

## ⚠️ Avoiding Common Mistakes

### **The "Patent Number" Rule**
When you give the AI a number, try to use the standard format: **Country Code + Number**.
*   ✅ **Correct:** `EP2933987` or `US.10123456.B2`
*   ❌ **Avoid:** `2933987` (Without the EP, the AI might get confused).

### **Wait for the Result**
Large reports (like the CCD or Full-text) take a few seconds to fetch because they come directly from the EPO in Europe. Just relax while the AI gathers the data for you!

### **Ask for "Plain English"**
Patent language is notoriously difficult. If the claims are too complex, just ask the AI: **"Can you explain these claims to me in simple, non-legal English?"**

---

*You now have a world-class patent research team at your command. Just ask a question and let the server do the rest!*

