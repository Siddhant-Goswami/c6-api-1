# ============================================
# STEP 22: MCP Client — Stdio and Streamable HTTP
# ============================================
#
# WHAT YOU'LL LEARN:
# - How to connect to an MCP server via Streamable HTTP
# - How to list and call tools, resources, and prompts from a client
# - The difference between stdio and HTTP client connections
#
# KEY IDEA:
#   Step 11 showed you the stdio client — it SPAWNED the server as a
#   subprocess and communicated over stdin/stdout.
#
#   Step 22 shows you the Streamable HTTP client — it connects to a
#   RUNNING server over the network. This is how real production clients
#   (Claude Desktop, Claude Code, third-party apps) connect to remote
#   MCP servers.
#
#   STDIO:    good for local use, server is a subprocess you launch
#   HTTP:     good for remote/production, server runs independently
#
#   Both use the same ClientSession API once connected.
#   The only difference is HOW the connection is established.
#
# REQUIRES:
#   Step 21 server must be running first!
#   In a separate terminal: python step21_mcp_http_server.py
#
# RUN THIS FILE:
#   python step22_mcp_http_client.py
#
# ============================================

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

print("=== Step 22: MCP Client — Stdio and Streamable HTTP ===")


# ============================================================
# PART 1: Streamable HTTP Client (connect to a running server)
# ============================================================

async def demo_http_client():
    """Connect to the step21 server running at localhost:8000."""
    server_url = "http://localhost:8000/mcp"

    print(f"\n[HTTP Client] Connecting to {server_url}...")

    # streamable_http_client returns 3 values: read stream, write stream, and
    # a getter for the initial HTTP response (rarely needed; we use _ for it)
    async with streamable_http_client(server_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:

            # REQUIRED first step — exchanges capability info with server
            await session.initialize()
            print("[HTTP Client] Connected and initialized!")

            # ─── Discover capabilities ───────────────────────────────────

            # List tools
            tools_result = await session.list_tools()
            print("\n[Tools]")
            for tool in tools_result.tools:
                print(f"  • {tool.name}: {tool.description}")

            # List resources
            resources_result = await session.list_resources()
            print("\n[Resources]")
            for resource in resources_result.resources:
                print(f"  • {resource.uri}: {resource.description}")

            # List prompts
            prompts_result = await session.list_prompts()
            print("\n[Prompts]")
            for prompt in prompts_result.prompts:
                print(f"  • {prompt.name}: {prompt.description}")

            # ─── Call tools ──────────────────────────────────────────────

            print("\n--- Calling 'add' tool ---")
            result = await session.call_tool("add", {"a": 7, "b": 35})
            # result.content is a list; [0] is the first (usually only) item
            # .text is the string value of a TextContent response
            print(f"  7 + 35 = {result.content[0].text}")

            print("\n--- Calling 'search_notes' tool ---")
            result = await session.call_tool("search_notes", {"query": "meeting"})
            print(f"  Results: {result.content[0].text}")

            # ─── Read resources ──────────────────────────────────────────

            print("\n--- Reading 'config://app' resource ---")
            result = await session.read_resource("config://app")
            # result.contents is a list of content blocks
            print(f"  Config:{result.contents[0].text}")

            print("\n--- Reading 'users://alice/profile' resource ---")
            result = await session.read_resource("users://alice/profile")
            print(f"  Profile: {result.contents[0].text}")

            # ─── Get a prompt ────────────────────────────────────────────

            print("\n--- Getting 'summarize_notes' prompt ---")
            result = await session.get_prompt(
                "summarize_notes",
                {"topic": "meeting", "style": "executive"},
            )
            # result.messages is a list of LLM message objects
            # Each message has a .content.text field
            print(f"  Prompt: {result.messages[0].content.text}")


# ============================================================
# PART 2: Stdio Client (spawns server as subprocess)
# ============================================================

async def demo_stdio_client():
    """Connect to the step21 server by spawning it as a subprocess."""
    print("\n[Stdio Client] Spawning server as subprocess...")

    # StdioServerParameters tells the client HOW to launch the server
    # The client will run: uv run step21_mcp_http_server.py stdio
    server_params = StdioServerParameters(
        command="python",
        args=["step21_mcp_http_server.py", "stdio"],
        env=None,  # inherit environment
    )

    # stdio_client spawns the subprocess and connects to it
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("[Stdio Client] Connected to subprocess server!")

            # Same API — the underlying transport doesn't matter once connected
            tools_result = await session.list_tools()
            print("\n[Tools via Stdio]")
            for tool in tools_result.tools:
                print(f"  • {tool.name}")

            result = await session.call_tool("add", {"a": 100, "b": 200})
            print(f"\n  100 + 200 = {result.content[0].text}")


# ============================================================
# PART 3: HTTP Client with Custom Headers
# ============================================================

async def demo_http_with_headers():
    """Connect with custom headers — useful for API key auth."""
    server_url = "http://localhost:8000/mcp"

    # Headers are passed directly to streamable_http_client.
    # Use this pattern when your server requires an API key or bearer token.
    headers = {
        "X-Custom-Header": "hello-from-client",
        # "Authorization": "Bearer your-token-here",  # for auth (step 23)
    }

    print("\n[HTTP Client with Headers] Connecting...")
    async with streamable_http_client(server_url, headers=headers) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            print("  Tools available:")
            for tool in tools_result.tools:
                print(f"    • {tool.name}")


# ============================================================
# Run the demos
# ============================================================

async def main():
    print("\n" + "="*50)
    print("DEMO 1: Streamable HTTP Client")
    print("="*50)
    print("(Make sure step21_mcp_http_server.py is running!)")
    try:
        await demo_http_client()
    except Exception as e:
        print(f"[!] HTTP client failed: {e}")
        print("    Is step21_mcp_http_server.py running?")
        print("    Run in another terminal: python step21_mcp_http_server.py")

    print("\n" + "="*50)
    print("DEMO 2: Stdio Client (spawns server)")
    print("="*50)
    try:
        await demo_stdio_client()
    except Exception as e:
        print(f"[!] Stdio client failed: {e}")

    print("\n" + "="*50)
    print("DEMO 3: HTTP Client with Custom Headers")
    print("="*50)
    try:
        await demo_http_with_headers()
    except Exception as e:
        print(f"[!] HTTP with headers failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())


# ============================================
# WHAT JUST HAPPENED:
#   DEMO 1 connected to the server running in another terminal via HTTP.
#   DEMO 2 spawned the server as a subprocess and connected via stdio.
#   DEMO 3 showed how to pass custom headers (used in step 23 for auth).
#
#   In all three cases, the CLIENT API is identical:
#     session.initialize()
#     session.list_tools()
#     session.call_tool(name, args)
#     session.list_resources()
#     session.read_resource(uri)
#     session.list_prompts()
#     session.get_prompt(name, args)
#
#   The TRANSPORT (how you connect) is the only difference.
#
# STDIO vs HTTP (when to use each):
#   stdio   → Claude Desktop config, local dev, subprocess tools
#   HTTP    → production servers, shared tools, remote deployments
#
# EXERCISE 1:
# Call 'search_notes' with query="todo" and print the result.
#
# EXERCISE 2:
# Read the resource 'users://bob/profile'. What do you get?
#
# EXERCISE 3:
# Get the 'summarize_notes' prompt with style="detailed".
# Compare the output to style="concise".
#
# EXERCISE 4:
# What happens if you call a tool that doesn't exist?
#   await session.call_tool("nonexistent_tool", {})
# What error does the SDK raise? How would you handle it?
# ============================================
