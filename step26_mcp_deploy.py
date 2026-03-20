# ============================================
# STEP 26: Deploying MCP Servers with Docker
# ============================================
#
# WHAT YOU'LL LEARN:
# - How to containerize an MCP server with Docker
# - How to connect Claude Desktop to a local or remote MCP server
# - Production deployment patterns (Cloud Run, Lambda, VPS)
# - The production checklist: security, reliability, performance
#
# KEY IDEA:
#   Steps 21-25 built and ran servers locally (python server.py).
#   That works for development, but production needs:
#     - Containerization: reproducible builds, consistent environments
#     - Port binding: accessible beyond localhost
#     - Process management: auto-restart on crash
#     - Configuration: env vars instead of hardcoded values
#
#   Docker handles all of this. Once containerized, your MCP server
#   deploys identically to any cloud platform: Cloud Run, ECS, Railway,
#   Render, Fly.io, or your own VPS.
#
# THIS FILE:
#   Unlike other steps, this is primarily DOCUMENTATION with runnable
#   demonstration code. The Docker/deployment config is shown as
#   print statements (since we can't create files with Docker commands here).
#
# RUN THIS FILE:
#   python step26_mcp_deploy.py
#   (This prints the Dockerfile, docker-compose.yml, and config snippets)
#
# ============================================

import os

print("=== Step 26: Deploying MCP Servers with Docker ===")


# ============================================================
# PART 1: Production-ready server (what goes in the Docker image)
# ============================================================

# This is the server you'd deploy. It reads config from environment variables
# and uses stateless HTTP mode for horizontal scaling.

# --- server_production.py (shown inline for reference) ---
PRODUCTION_SERVER_CODE = '''
"""Production MCP server — reads config from env, stateless HTTP."""
import os
import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Production Server",
    json_response=True,
    stateless_http=True,   # Safe for multiple replicas
)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def get_environment() -> dict:
    """Return current environment info (useful for debugging deployments)."""
    return {
        "env": os.environ.get("MCP_ENV", "development"),
        "version": os.environ.get("APP_VERSION", "unknown"),
        "region": os.environ.get("REGION", "local"),
    }


if __name__ == "__main__":
    # Cloud Run / Lambda: PORT env var is set by the platform
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"  # IMPORTANT: must bind to 0.0.0.0 in containers
    transport = sys.argv[1] if len(sys.argv) > 1 else "streamable-http"
    mcp.run(transport=transport, host=host, port=port)
'''

print("\n--- server_production.py ---")
print(PRODUCTION_SERVER_CODE)


# ============================================================
# PART 2: Dockerfile
# ============================================================

DOCKERFILE = '''# ---- Dockerfile ----
FROM python:3.12-slim

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first (for Docker layer caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies (--frozen: use exact versions from lockfile)
RUN uv sync --frozen --no-dev

# Copy application code
COPY server_production.py ./

# Expose the MCP port
EXPOSE 8000

# Run the server
# uv run: uses the project's virtual environment automatically
CMD ["uv", "run", "server_production.py"]
'''

print("--- Dockerfile ---")
print(DOCKERFILE)


# ============================================================
# PART 3: docker-compose.yml
# ============================================================

DOCKER_COMPOSE = '''# ---- docker-compose.yml ----
version: "3.9"

services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"         # host:container
    environment:
      - MCP_ENV=production
      - APP_VERSION=1.0.0
      # Uncomment for authenticated servers (step 23):
      # - MCP_AUTH_TOKEN_SECRET=your-signing-key
      # - OAUTH_ISSUER_URL=https://your-auth-provider.com
    healthcheck:
      # Verify the server is responding before marking as healthy
      test: ["CMD", "curl", "-f", "http://localhost:8000/mcp"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped   # Auto-restart on crash
'''

print("--- docker-compose.yml ---")
print(DOCKER_COMPOSE)


# ============================================================
# PART 4: Build and test commands
# ============================================================

print("\n--- Build & Test Commands ---")
commands = [
    ("Build the container",        "docker compose build"),
    ("Start in background",        "docker compose up -d"),
    ("View logs",                  "docker compose logs -f mcp-server"),
    ("Test with HTTP client",      "python step22_mcp_http_client.py"),
    ("Test with Inspector",        "npx @modelcontextprotocol/inspector"),
    ("Stop",                       "docker compose down"),
    ("Rebuild after code change",  "docker compose up -d --build"),
]
for description, cmd in commands:
    print(f"  # {description}")
    print(f"  {cmd}\n")


# ============================================================
# PART 5: Claude Desktop configuration
# ============================================================

print("--- Claude Desktop Config ---")
print("macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
print("Windows: %APPDATA%\\\\Claude\\\\claude_desktop_config.json\n")

CLAUDE_DESKTOP_LOCAL = '''{
  "mcpServers": {
    "my-local-server": {
      "command": "python",
      "args": [
        "/absolute/path/to/step21_mcp_http_server.py",
        "stdio"
      ]
    }
  }
}'''

CLAUDE_DESKTOP_REMOTE = '''{
  "mcpServers": {
    "my-remote-server": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://your-server.example.com/mcp"
      ]
    }
  }
}'''

print("For LOCAL servers (stdio):")
print(CLAUDE_DESKTOP_LOCAL)
print("\nFor REMOTE servers (Streamable HTTP via mcp-remote adapter):")
print(CLAUDE_DESKTOP_REMOTE)


# ============================================================
# PART 6: Deployment platform comparison
# ============================================================

print("\n--- Deployment Platforms ---")
platforms = [
    ("Docker / VPS",          "Full control, always running", "None",      "Most flexible, SSH access"),
    ("Google Cloud Run",      "Auto-scaling, pay-per-use",    "~2-5s",     "Add stateless_http=True"),
    ("Cloudflare Workers",    "Edge, ultra-low latency",      "Near-zero", "Python Workers supported"),
    ("AWS Lambda + API GW",   "Enterprise serverless",        "~1-3s",     "More config overhead"),
    ("Railway / Render",      "Simple Git-based deploy",      "None",      "Great for prototypes"),
]

print(f"  {'Platform':<28} {'Best For':<30} {'Cold Start':<12} {'Notes'}")
print(f"  {'-'*28} {'-'*30} {'-'*12} {'-'*30}")
for platform, best_for, cold_start, notes in platforms:
    print(f"  {platform:<28} {best_for:<30} {cold_start:<12} {notes}")


# ============================================================
# PART 7: Production checklist
# ============================================================

print("\n--- Production Checklist ---")

checklist = {
    "Security": [
        "Enable OAuth 2.1 or token verification for all remote servers (step 23)",
        "Validate the Origin header (spec requirement for Streamable HTTP)",
        "Use HTTPS — terminate TLS at load balancer or reverse proxy",
        "Implement rate limiting to prevent abuse from LLM loops",
        "Scope tool permissions — don't expose destructive ops without guardrails",
    ],
    "Reliability": [
        "Use stateless_http=True for horizontally scaled deployments",
        "Add health check endpoints (Docker HEALTHCHECK, cloud platform checks)",
        "Implement error handling in tools — return error strings, don't crash",
        "Set up structured logging (JSON logs for log aggregation services)",
        "Use lifespan management for DB connections (step 25)",
    ],
    "Performance": [
        "Use json_response=True for cleaner structured responses",
        "Cache expensive tool results where appropriate",
        "Set appropriate timeouts for external API calls within tools",
        "Add CORS headers if browser-based MCP clients will connect",
    ],
    "Testing": [
        "Test with MCP Inspector before deploying",
        "Write integration tests using the SDK's client classes",
        "Test both stdio and HTTP transports",
        "Verify authentication flows end-to-end (step 23-24)",
    ],
}

for section, items in checklist.items():
    print(f"\n  [{section}]")
    for item in items:
        print(f"  [ ] {item}")


# ============================================================
# PART 8: Quick reference — key server config patterns
# ============================================================

print("\n--- Quick Reference: Server Config Patterns ---")
print("""
  # Local dev (stdio, no auth):
  mcp = FastMCP("Dev Server")
  mcp.run(transport="stdio")

  # Remote dev (HTTP, no auth):
  mcp = FastMCP("Dev Server", json_response=True)
  mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)

  # Production (HTTP, stateless, auth):
  mcp = FastMCP(
      "Prod Server",
      json_response=True,
      stateless_http=True,
      token_verifier=MyTokenVerifier(),
      auth=AuthSettings(issuer_url=..., resource_server_url=...),
  )
  port = int(os.environ.get("PORT", 8000))
  mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
""")

print("=== Deployment summary complete ===")
print("Next steps:")
print("  1. Create a Dockerfile in your project directory")
print("  2. Run: docker compose up -d")
print("  3. Connect with MCP Inspector or step22_mcp_http_client.py")
print("  4. Add Claude Desktop config to use the server in Claude")


# ============================================
# WHAT YOU'VE BUILT (Steps 21-26):
#
#   Step 21: MCP Server with tools, resources, prompts over HTTP
#   Step 22: MCP Client — stdio and Streamable HTTP
#   Step 23: Authentication server with Token Verification
#   Step 24: Authentication client with bearer tokens
#   Step 25: Advanced patterns — lifespan, progress, structured output, stateless
#   Step 26: Docker deployment + Claude Desktop config + production checklist
#
# FULL PICTURE:
#   Steps 10-13: MCP basics with stdio (local, no auth)
#   Steps 21-26: MCP production with HTTP, auth, advanced patterns, Docker
#
# WHERE TO GO NEXT:
#   - Deploy to Google Cloud Run or Railway for a real remote server
#   - Integrate with your actual database via lifespan (step 25 pattern)
#   - Set up a real OAuth provider (Auth0 free tier) instead of the demo token
#   - Build an MCP server for your own data or API and add it to Claude Desktop
#
# EXERCISE 1:
# Create a Dockerfile from the template in Part 2 and build it.
# Run: docker compose up -d
# Connect the MCP Inspector to http://localhost:8000/mcp.
#
# EXERCISE 2:
# Add this server to your Claude Desktop config (Part 5).
# Ask Claude: "What tools do you have available?"
# See your tools appear in Claude's tool picker.
#
# EXERCISE 3 (capstone):
# Build a production-ready MCP server that:
# - Exposes 3+ tools relevant to your work
# - Uses lifespan for any shared resources
# - Requires bearer token authentication
# - Is deployable via Docker
# ============================================
