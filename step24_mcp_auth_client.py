# ============================================
# STEP 24: MCP Auth Client — Sending Bearer Tokens
# ============================================
#
# WHAT YOU'LL LEARN:
# - How to send a bearer token from an MCP client
# - How OAuth token storage works for full OAuth flows
# - How to handle 401 errors gracefully
#
# KEY IDEA:
#   Step 23 built a server that REQUIRES authentication.
#   Step 24 shows how the CLIENT sends the token.
#
#   There are two patterns:
#
#   A) SIMPLE: Pass token in headers (for Token Verifier servers)
#      → You already have the token (from env var, config, etc.)
#      → Just pass: headers={"Authorization": "Bearer <token>"}
#      → This is what most production setups use
#
#   B) FULL OAUTH FLOW: OAuthClientProvider (for OAuth Authorization Servers)
#      → The server runs its own OAuth AS (less common)
#      → Client redirects to browser, user logs in, gets code, exchanges for token
#      → SDK's OAuthClientProvider handles this automatically
#
#   For step 23's Token Verifier server, Pattern A is correct.
#   This step shows both, but focuses on Pattern A.
#
# REQUIRES:
#   Step 23 server must be running first!
#   In a separate terminal: python step23_mcp_auth_server.py
#
# RUN THIS FILE:
#   python step24_mcp_auth_client.py
# ============================================

import asyncio
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

print("=== Step 24: MCP Auth Client — Sending Bearer Tokens ===")


# ============================================================
# PART 1: Simple Bearer Token (most common production pattern)
# ============================================================

async def demo_bearer_token():
    """
    Connect to the authenticated server using a bearer token.
    This is the go-to pattern for production: you have a token
    (from an env var, a secrets manager, etc.) and you send it.
    """
    server_url = "http://localhost:8001/mcp"

    # Get token from environment variable in production.
    # For this demo, we use the hardcoded value from step 23.
    token = os.environ.get("MCP_AUTH_TOKEN", "demo-secret-token-12345")

    print(f"\n[Pattern A] Connecting with bearer token...")
    print(f"  Token: {token[:20]}...")

    # Pass the token as an Authorization header.
    # The server's TokenVerifier will validate it.
    headers = {"Authorization": f"Bearer {token}"}

    async with streamable_http_client(server_url, headers=headers) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            print("  Connected and authenticated!")

            # List available tools
            tools_result = await session.list_tools()
            print("\n  [Authenticated Tools]")
            for tool in tools_result.tools:
                print(f"    • {tool.name}: {tool.description}")

            # Call protected tool
            print("\n  --- Calling 'list_categories' ---")
            result = await session.call_tool("list_categories", {})
            print(f"  Categories: {result.content[0].text}")

            print("\n  --- Calling 'get_secret_data' (billing) ---")
            result = await session.call_tool(
                "get_secret_data", {"category": "billing"}
            )
            print(f"  Data: {result.content[0].text}")

            # Read protected resource
            print("\n  --- Reading 'secrets://overview' ---")
            result = await session.read_resource("secrets://overview")
            print(f"  Overview: {result.contents[0].text}")


# ============================================================
# PART 2: What happens with an invalid token?
# ============================================================

async def demo_invalid_token():
    """Show what happens when we send a wrong token."""
    server_url = "http://localhost:8001/mcp"
    bad_token = "this-is-not-a-valid-token"

    print(f"\n[Pattern A — Invalid Token] Connecting with bad token...")

    headers = {"Authorization": f"Bearer {bad_token}"}

    try:
        async with streamable_http_client(server_url, headers=headers) as (r, w, _):
            async with ClientSession(r, w) as session:
                # initialize() triggers the first authenticated request
                await session.initialize()
                print("  [!] This shouldn't succeed with an invalid token")
    except Exception as e:
        # The SDK will raise an exception when the server returns 401
        print(f"  Expected auth error: {type(e).__name__}: {e}")
        print("  The server correctly rejected the invalid token.")


# ============================================================
# PART 3: What happens with no token at all?
# ============================================================

async def demo_no_token():
    """Show what happens when we send no Authorization header."""
    server_url = "http://localhost:8001/mcp"

    print(f"\n[Pattern A — No Token] Connecting without any token...")

    try:
        # No headers at all
        async with streamable_http_client(server_url) as (r, w, _):
            async with ClientSession(r, w) as session:
                await session.initialize()
                print("  [!] This shouldn't succeed without a token")
    except Exception as e:
        print(f"  Expected auth error: {type(e).__name__}: {e}")
        print("  The server correctly rejected the unauthenticated request.")


# ============================================================
# PART 4: OAuthClientProvider (full OAuth flow — for reference)
# ============================================================

# This is the full OAuth 2.1 flow for servers that run their own
# Authorization Server (not covered in this course, shown for completeness).
#
# from urllib.parse import parse_qs, urlparse
# from pydantic import AnyUrl
# from mcp.client.auth import OAuthClientProvider, TokenStorage
# from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken
#
# class InMemoryTokenStorage(TokenStorage):
#     def __init__(self):
#         self.tokens = None
#         self.client_info = None
#
#     async def get_tokens(self): return self.tokens
#     async def set_tokens(self, tokens): self.tokens = tokens
#     async def get_client_info(self): return self.client_info
#     async def set_client_info(self, info): self.client_info = info
#
# async def handle_redirect(url: str) -> str:
#     print(f"Open this URL: {url}")
#     callback = input("Paste callback URL: ")
#     params = parse_qs(urlparse(callback).query)
#     return params["code"][0]
#
# oauth_provider = OAuthClientProvider(
#     server_url=server_url,
#     client_metadata=OAuthClientMetadata(
#         client_name="My App",
#         redirect_uris=[AnyUrl("http://localhost:3000/callback")],
#         grant_types=["authorization_code", "refresh_token"],
#         response_types=["code"],
#     ),
#     storage=InMemoryTokenStorage(),
#     redirect_handler=handle_redirect,
# )
# Then pass oauth_provider= to streamable_http_client.


# ============================================================
# Run the demos
# ============================================================

async def main():
    print("(Make sure step23_mcp_auth_server.py is running!)")
    print("Run in another terminal: python step23_mcp_auth_server.py")

    print("\n" + "="*50)
    print("DEMO 1: Valid bearer token")
    print("="*50)
    try:
        await demo_bearer_token()
    except Exception as e:
        print(f"[!] Failed: {e}")
        print("    Is step23_mcp_auth_server.py running on port 8001?")

    print("\n" + "="*50)
    print("DEMO 2: Invalid token (expect rejection)")
    print("="*50)
    try:
        await demo_invalid_token()
    except Exception as e:
        print(f"  Caught error: {e}")

    print("\n" + "="*50)
    print("DEMO 3: No token at all (expect rejection)")
    print("="*50)
    try:
        await demo_no_token()
    except Exception as e:
        print(f"  Caught error: {e}")


if __name__ == "__main__":
    asyncio.run(main())


# ============================================
# WHAT JUST HAPPENED:
#   Demo 1: Valid token → server accepts → tools work
#   Demo 2: Invalid token → server returns 401 → SDK raises exception
#   Demo 3: No token → server returns 401 → SDK raises exception
#
#   The client's job is simple:
#     1. Get a valid token (from env, secrets manager, etc.)
#     2. Pass it as: headers={"Authorization": "Bearer <token>"}
#     3. Handle exceptions for auth failures (retry, refresh, etc.)
#
#   In production, you'd typically:
#     - Store the token in an environment variable
#     - Refresh it when it expires (OAuth refresh token flow)
#     - Log auth failures for monitoring
#
# PRODUCTION TOKEN PATTERN:
#   token = os.environ["MCP_AUTH_TOKEN"]       # from secrets manager
#   headers = {"Authorization": f"Bearer {token}"}
#   # That's it. The rest is the same as unauthenticated usage.
#
# EXERCISE 1:
# Set the environment variable and use it:
#   export MCP_AUTH_TOKEN=demo-secret-token-12345
#   python step24_mcp_auth_client.py
# Notice how the code already reads from MCP_AUTH_TOKEN.
#
# EXERCISE 2:
# Add error handling for expired tokens:
#   try:
#       result = await session.call_tool(...)
#   except Exception as e:
#       if "401" in str(e) or "unauthorized" in str(e).lower():
#           print("Token expired — refreshing...")
#           # refresh token logic here
#
# EXERCISE 3:
# Call 'get_secret_data' with category="api_keys".
# Then call it with category="nonexistent" — what does the server return?
# ============================================
