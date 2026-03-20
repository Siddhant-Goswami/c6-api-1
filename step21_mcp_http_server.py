# ============================================
# STEP 21: MCP Server — Resources, Prompts, and HTTP Transport
# ============================================
#
# WHAT YOU'LL LEARN:
# - How to expose Resources (readable data) and Prompts (reusable templates)
# - How Streamable HTTP transport differs from stdio
# - Why the official `mcp` SDK replaces the standalone `fastmcp` package
#
# KEY IDEA:
#   Steps 10-13 used `fastmcp` (standalone) over stdio transport.
#   The MCP specification has since evolved. The official Python SDK
#   now bundles FastMCP and adds Streamable HTTP — the standard for
#   remote, production-ready MCP servers.
#
#   MCP has THREE primitives:
#     Tools     — functions the LLM can CALL  (like POST endpoints)
#     Resources — data the LLM can READ       (like GET endpoints)
#     Prompts   — reusable templates for LLM interactions
#
#   This step shows all three running over Streamable HTTP.
#
# INSTALL:
#   pip install "mcp[cli]"
#   (This installs the official SDK with FastMCP bundled inside)
#
# RUN THIS FILE:
#   python step21_mcp_http_server.py
#
# Then inspect it:
#   npx @modelcontextprotocol/inspector
#   Connect to: http://localhost:8000/mcp
# ============================================

import sys
from mcp.server.fastmcp import FastMCP

# ============================================================
# PART 1: Create the server
# ============================================================

# json_response=True is recommended for Streamable HTTP deployments.
# It ensures responses are well-formed JSON rather than raw text streams.
mcp = FastMCP("Tutorial Server", json_response=True)

print("=== Step 21: MCP Server with Resources, Prompts, and HTTP ===")


# ============================================================
# PART 2: Tools (you already know these from steps 10-13)
# ============================================================

# Tools are functions the LLM can CALL.
# The LLM decides WHEN to call them based on user intent.

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    print(f"[tool] add({a}, {b})")
    return a + b


@mcp.tool()
def search_notes(query: str) -> str:
    """Search through user notes by keyword."""
    print(f"[tool] search_notes('{query}')")
    # Simulated note database
    notes = {
        "meeting":  "Team standup at 10am. Discuss Q1 roadmap.",
        "todo":     "Fix authentication bug. Review PR #42.",
        "idea":     "Build an MCP server for the internal wiki.",
    }
    results = [
        f"[{key}]: {val}"
        for key, val in notes.items()
        if query.lower() in key.lower() or query.lower() in val.lower()
    ]
    return "\n".join(results) if results else f"No notes matching '{query}'."


# ============================================================
# PART 3: Resources — data the LLM can READ
# ============================================================

# Resources are like GET endpoints. The LLM or client can READ them
# to get context, configuration, or any data.
#
# Key difference from tools:
#   Tools    — the LLM CALLS them to take action or fetch dynamic data
#   Resources— clients READ them to provide context (think: file contents)
#
# Resources use URI templates: "scheme://path/{param}"

@mcp.resource("config://app")
def get_app_config() -> str:
    """Return the current application configuration."""
    print("[resource] reading config://app")
    return """
app_name: Tutorial App
version: 1.0.0
environment: development
max_results: 50
"""


@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Get a user's profile by their ID.

    The {user_id} in the URI is automatically extracted and passed as an argument.
    Example: reading 'users://alice/profile' calls this with user_id='alice'
    """
    print(f"[resource] reading users://{user_id}/profile")
    profiles = {
        "alice": "Alice Chen — Engineering Lead, joined 2022",
        "bob":   "Bob Kumar — Product Manager, joined 2023",
    }
    return profiles.get(user_id, f"User '{user_id}' not found.")


# ============================================================
# PART 4: Prompts — reusable LLM interaction templates
# ============================================================

# Prompts are templates that generate well-formed instructions for the LLM.
# They're useful when you have a common task pattern that clients want to reuse.
#
# Example: a "summarize this document" prompt with customizable style.
# The client calls get_prompt("summarize_notes", {...}) and gets back
# a ready-to-send message that includes the user's parameters.

@mcp.prompt()
def summarize_notes(topic: str, style: str = "concise") -> str:
    """Generate a prompt for summarizing notes on a topic.

    Args:
        topic: The subject to summarize notes about.
        style: Output style — 'concise', 'detailed', or 'executive'.
    """
    print(f"[prompt] summarize_notes(topic='{topic}', style='{style}')")
    styles = {
        "concise":   "in 2-3 bullet points",
        "detailed":  "with full context and action items",
        "executive": "as a one-paragraph executive summary",
    }
    qualifier = styles.get(style, styles["concise"])
    return f"Summarize all notes related to '{topic}' {qualifier}."


# ============================================================
# PART 5: Run the server
# ============================================================

if __name__ == "__main__":
    # Accept transport as a command-line argument so we can run
    # both HTTP (default) and stdio (for Claude Desktop / step 22 client tests)
    transport = sys.argv[1] if len(sys.argv) > 1 else "streamable-http"

    print(f"Starting server with transport: {transport}")

    if transport == "streamable-http":
        print("Server running at: http://localhost:8000/mcp")
        print("Inspect with: npx @modelcontextprotocol/inspector")
    else:
        print("Server running in stdio mode (waiting for client connection)")

    mcp.run(transport=transport)


# ============================================
# WHAT JUST HAPPENED:
#   This server exposes all three MCP primitives:
#     - Tools:     add, search_notes
#     - Resources: config://app, users://{user_id}/profile
#     - Prompts:   summarize_notes
#
#   Over Streamable HTTP, the server listens at /mcp
#   (vs stdio in steps 10-13, where there was no HTTP endpoint)
#
# TOOLS vs RESOURCES vs PROMPTS (summary):
#   Tools     → LLM calls to DO something or fetch dynamic/computed data
#   Resources → Client reads to GET static/contextual data (like a file)
#   Prompts   → Templates that assemble LLM message content from parameters
#
# COMPARE:
#   Step 10 used `from fastmcp import FastMCP` (standalone package)
#   Step 21 uses `from mcp.server.fastmcp import FastMCP` (official SDK)
#   The API is nearly identical — FastMCP is now bundled inside `mcp`.
#
# EXERCISE 1:
# Add a resource that lists all available note keys:
#   @mcp.resource("notes://index")
#   def list_notes() -> str:
#       return "\n".join(["meeting", "todo", "idea"])
# Inspect it in the MCP Inspector.
#
# EXERCISE 2:
# Add a prompt for drafting a reply to a note:
#   @mcp.prompt()
#   def draft_reply(note_key: str, tone: str = "professional") -> str:
#       return f"Draft a {tone} reply to the '{note_key}' note."
#
# EXERCISE 3:
# What happens when you request a resource URI that has a typo?
# Try reading 'users://charlie/profile' — trace through the code.
# ============================================
