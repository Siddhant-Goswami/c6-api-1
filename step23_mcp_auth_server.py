# ============================================
# STEP 23: MCP Authentication — Token Verification
# ============================================
#
# WHAT YOU'LL LEARN:
# - Why MCP servers need authentication for production use
# - The Token Verifier pattern (Resource Server)
# - How to validate bearer tokens before allowing tool access
# - How to test authenticated endpoints
#
# KEY IDEA:
#   Steps 21-22 built servers with NO authentication.
#   Anyone on the network could call your tools. That's fine for local dev,
#   but dangerous in production.
#
#   MCP supports OAuth 2.1 for authentication. The most practical pattern
#   for production is the "Token Verifier" (Resource Server) pattern:
#
#     1. Your auth provider (Auth0, Okta, Cognito, etc.) issues tokens
#     2. Clients include: Authorization: Bearer <token> in every request
#     3. Your MCP server validates the token before processing requests
#
#   You implement ONE method: verify_token(token) -> AccessToken | None
#   If it returns None, the request is rejected with 401 Unauthorized.
#
#   This step: hardcoded demo token (so you can test without a real auth provider)
#   Step 24: client sends the token
#   Production: replace verify_token with real JWT validation
#
# INSTALL:
#   pip install "mcp[cli]" pydantic
#
# RUN THIS FILE:
#   python step23_mcp_auth_server.py
#
# Then test:
#   npx @modelcontextprotocol/inspector
#   Connect to http://localhost:8001/mcp
#   In Inspector: OAuth Settings -> set Bearer Token = demo-secret-token-12345
# ============================================

import sys
from pydantic import AnyHttpUrl
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP

print("=== Step 23: MCP Authentication — Token Verification ===")


# ============================================================
# PART 1: Implement your Token Verifier
# ============================================================

class MyTokenVerifier(TokenVerifier):
    """
    Validates bearer tokens before allowing access to MCP tools.

    In production, this would:
    1. Fetch the auth provider's JWKS (JSON Web Key Set)
    2. Verify the JWT signature
    3. Check claims: audience, issuer, expiry, scopes
    4. Return an AccessToken if valid, None if invalid

    For this demo: we accept one hardcoded token.
    """

    async def verify_token(self, token: str) -> AccessToken | None:
        print(f"[auth] Verifying token: {token[:20]}...")

        # ─── DEMO: Accept a single hardcoded token ───────────────────────
        # NEVER do this in production! This is only for learning.
        if token == "demo-secret-token-12345":
            print("[auth] Token valid! Granting access.")
            return AccessToken(
                token=token,
                client_id="demo-client",
                scopes=["read", "write"],
                expires_at=None,   # None means "never expires" (demo only)
            )

        # ─── PRODUCTION PATTERN (commented out) ──────────────────────────
        # This is how you'd validate a real JWT from Auth0/Okta/Cognito:
        #
        # import jwt
        # import httpx
        #
        # JWKS_URL  = "https://your-auth0-domain.auth0.com/.well-known/jwks.json"
        # ISSUER    = "https://your-auth0-domain.auth0.com/"
        # AUDIENCE  = "http://localhost:8001"
        #
        # try:
        #     # Fetch public keys from auth provider
        #     jwks_client = jwt.PyJWKClient(JWKS_URL)
        #     signing_key = jwks_client.get_signing_key_from_jwt(token)
        #
        #     # Verify signature, expiry, audience, issuer all at once
        #     payload = jwt.decode(
        #         token,
        #         signing_key.key,
        #         algorithms=["RS256"],
        #         audience=AUDIENCE,
        #         issuer=ISSUER,
        #     )
        #     return AccessToken(
        #         token=token,
        #         client_id=payload.get("sub", "unknown"),
        #         scopes=payload.get("scope", "").split(),
        #         expires_at=payload.get("exp"),
        #     )
        # except jwt.InvalidTokenError as e:
        #     print(f"[auth] Invalid token: {e}")
        #     return None
        # ─────────────────────────────────────────────────────────────────

        print("[auth] Token invalid — rejecting request.")
        return None   # → client receives 401 Unauthorized


# ============================================================
# PART 2: Create the authenticated server
# ============================================================

# AuthSettings configure the RFC 9728 Protected Resource Metadata endpoint.
# This tells OAuth clients WHERE to get tokens and WHO issued them.
mcp = FastMCP(
    "Authenticated Tutorial Server",
    json_response=True,
    # Attach the verifier — every request will be checked
    token_verifier=MyTokenVerifier(),
    host="0.0.0.0",
    port=8001,
    # Auth metadata (published at /.well-known/oauth-protected-resource)
    auth=AuthSettings(
        issuer_url=AnyHttpUrl("https://auth.example.com"),           # Your auth provider
        resource_server_url=AnyHttpUrl("http://localhost:8001"),      # This server
        required_scopes=["read"],                                     # Minimum scopes
    ),
)


# ============================================================
# PART 3: Protected tools and resources
# ============================================================

# These tools are now PROTECTED — callers must present a valid bearer token.
# The token verification happens automatically before any tool is called.

@mcp.tool()
def get_secret_data(category: str) -> str:
    """Retrieve sensitive data (requires authentication).

    Args:
        category: One of 'api_keys', 'billing', or 'users'.
    """
    print(f"[tool] get_secret_data(category='{category}')")
    secrets = {
        "api_keys": "sk-live-abc123... (3 active keys)",
        "billing":  "Current plan: Enterprise, $4,200/mo",
        "users":    "1,247 active users, 89 admins",
    }
    return secrets.get(category, f"No data for category '{category}'.")


@mcp.tool()
def list_categories() -> list[str]:
    """List available secret data categories."""
    print("[tool] list_categories()")
    return ["api_keys", "billing", "users"]


@mcp.resource("secrets://overview")
def secrets_overview() -> str:
    """Overview of available secret categories (requires authentication)."""
    print("[resource] reading secrets://overview")
    return "Available categories: api_keys, billing, users"


# ============================================================
# PART 4: Run
# ============================================================

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "streamable-http"

    print(f"Starting authenticated server on port 8001 ({transport})")
    print("Required token: demo-secret-token-12345")
    print("Endpoint: http://localhost:8001/mcp")
    print()
    print("Test with curl:")
    print('  curl -H "Authorization: Bearer demo-secret-token-12345" \\')
    print('       -X POST http://localhost:8001/mcp')

    mcp.run(transport=transport)


# ============================================
# WHAT JUST HAPPENED:
#   1. MyTokenVerifier.verify_token() is called for EVERY request
#   2. If the token is invalid (or missing), the server returns 401
#   3. If valid, verify_token returns an AccessToken with scopes
#   4. The tool executes normally
#
#   The auth flow:
#     Client → "Authorization: Bearer abc123" → server
#     Server → verify_token("abc123") → AccessToken or None
#     None   → 401 Unauthorized
#     Token  → tool runs → response
#
# WHY TOKEN VERIFIER PATTERN (vs rolling your own OAuth)?
#   Your auth provider (Auth0, Cognito, etc.) handles:
#     - User login UI
#     - Token issuance + rotation
#     - MFA, social login, etc.
#   Your MCP server ONLY needs to VALIDATE tokens — much simpler.
#
# NEXT STEP:
#   Run this server, then run step24_mcp_auth_client.py
#   to see how the client sends the bearer token.
#
# EXERCISE 1:
# Add a scope check inside verify_token:
#   if "write" not in token_scopes_from_db:
#       return None  # Reject read-only tokens for write operations
#
# EXERCISE 2:
# Try connecting with the MCP Inspector WITHOUT setting a bearer token.
# What error do you get? What HTTP status code?
#
# EXERCISE 3:
# Add a tool that only allows the "billing" category if the token
# has scope "billing:read" (hint: check the AccessToken.scopes field).
# ============================================
