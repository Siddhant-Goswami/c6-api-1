# ============================================
# STEP 25: Advanced MCP Patterns
# ============================================
#
# WHAT YOU'LL LEARN:
# - Lifespan management: set up and tear down shared resources (DB pools, etc.)
# - Progress reporting: tell clients how far along a long operation is
# - Structured output: return dicts/objects for richer tool responses
# - Stateless HTTP mode: run multiple server replicas for horizontal scaling
#
# KEY IDEA:
#   The basics (tools, resources, prompts) cover 90% of use cases.
#   These patterns cover the remaining 10% that production systems need:
#
#   LIFESPAN: Your tools often need shared resources — a DB connection pool,
#   an ML model loaded into memory, an external API client. You DON'T want
#   to create these inside every tool call (too slow). Lifespan lets you
#   create them ONCE on startup and clean up on shutdown.
#
#   PROGRESS: Long-running tools (file processing, batch jobs) should
#   report progress so the client/user isn't left wondering what's happening.
#
#   STRUCTURED OUTPUT: Returning a dict auto-generates a JSON schema,
#   giving clients richer, typed data instead of just strings.
#
#   STATELESS HTTP: Required when running behind a load balancer.
#   Each request is handled independently — no session state stored.
#
# RUN THIS FILE:
#   python step25_mcp_advanced.py
#
# Then inspect at: http://localhost:8002/mcp
# ============================================

import asyncio
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP

print("=== Step 25: Advanced MCP Patterns ===")


# ============================================================
# PART 1: Lifespan — set up shared resources on startup
# ============================================================

@dataclass
class AppContext:
    """
    Type-safe container for resources shared across all tool calls.

    In production this might hold:
    - db_pool: asyncpg.Pool or SQLAlchemy AsyncSession
    - http_client: httpx.AsyncClient (reuse connections)
    - ml_model: a loaded sentence-transformer or similar
    - cache: a Redis client
    """
    db_pool: dict      # Simulated DB connection pool
    http_client: dict  # Simulated HTTP client


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Called ONCE when the server starts. Yields the shared context.
    The finally block runs when the server shuts down.

    Usage: tools access it via ctx.request_context.lifespan_context
    """
    print("[lifespan] Starting up — connecting to database...")

    # Simulate expensive startup (real code: await asyncpg.create_pool(...))
    db_pool = {"connection": "active", "pool_size": 10}

    print("[lifespan] Starting up — creating HTTP client...")
    http_client = {"session": "active", "timeout": 30}

    try:
        # Everything your tools need is passed via AppContext
        yield AppContext(db_pool=db_pool, http_client=http_client)
    finally:
        # This runs on graceful shutdown
        print("[lifespan] Shutting down — closing DB pool...")
        db_pool.clear()
        print("[lifespan] Shutting down — closing HTTP client...")
        http_client.clear()


# Create server with lifespan management
mcp = FastMCP(
    "Advanced Patterns Server",
    json_response=True,
    lifespan=app_lifespan,
    stateless_http=True,   # See Part 4 for explanation
)


# ============================================================
# PART 2: Tools that use the shared context
# ============================================================

@mcp.tool()
async def query_database(sql: str, ctx: Context) -> str:
    """
    Execute a read-only database query.

    The 'ctx: Context' parameter is SPECIAL — FastMCP injects it automatically.
    It gives you access to lifespan resources, logging, and progress reporting.
    You do NOT pass it when calling the tool from a client.
    """
    print(f"[tool] query_database('{sql}')")

    # Access the shared AppContext created in app_lifespan
    app_ctx: AppContext = ctx.request_context.lifespan_context
    db = app_ctx.db_pool

    # Log a message visible in the client/inspector
    ctx.info(f"Executing query against pool (status: {db['connection']})")

    # Simulate query result
    return f"Query '{sql}' executed on pool (size={db['pool_size']}). Rows: 42"


@mcp.tool()
async def fetch_external_api(endpoint: str, ctx: Context) -> str:
    """Fetch data from an external API using the shared HTTP client."""
    print(f"[tool] fetch_external_api('{endpoint}')")

    app_ctx: AppContext = ctx.request_context.lifespan_context
    client = app_ctx.http_client

    ctx.info(f"Using persistent HTTP client (timeout={client['timeout']}s)")

    # In production: await app_ctx.http_client.get(endpoint)
    return f"GET {endpoint} → 200 OK (simulated, client reused)"


# ============================================================
# PART 3: Progress reporting for long-running tools
# ============================================================

@mcp.tool()
async def process_files(file_paths: list[str], ctx: Context) -> str:
    """
    Process multiple files and report progress.

    Progress updates appear in supporting MCP clients (like Claude Desktop).
    The ctx.info() messages appear as logs in the MCP Inspector.

    Args:
        file_paths: List of file paths to process.
    """
    print(f"[tool] process_files({len(file_paths)} files)")
    total = len(file_paths)

    for i, path in enumerate(file_paths):
        # Log what we're currently doing
        ctx.info(f"Processing file {i+1}/{total}: {path}")

        # Report progress: (current, total)
        # Clients can use this to show a progress bar
        await ctx.report_progress(i, total)

        # Simulate work
        await asyncio.sleep(0.3)

    # Signal 100% complete
    await ctx.report_progress(total, total)

    return f"Processed {total} files successfully."


@mcp.tool()
async def long_running_analysis(data_size: int, ctx: Context) -> str:
    """
    Simulate a multi-stage analysis with progress milestones.

    Args:
        data_size: Number of records to process (simulated).
    """
    print(f"[tool] long_running_analysis(data_size={data_size})")
    stages = ["Loading data", "Cleaning", "Analyzing", "Generating report"]

    for i, stage in enumerate(stages):
        ctx.info(f"Stage {i+1}/{len(stages)}: {stage}...")
        await ctx.report_progress(i, len(stages))
        await asyncio.sleep(0.5)

    await ctx.report_progress(len(stages), len(stages))
    return f"Analysis of {data_size} records complete. 4 stages finished."


# ============================================================
# PART 4: Structured output — return rich typed data
# ============================================================

@mcp.tool()
def get_weather(city: str) -> dict:
    """
    Get weather for a city.

    Returning a dict (or Pydantic model) instead of a string gives clients:
    1. A JSON schema generated from the return type
    2. Structured data they can parse programmatically
    3. Better type safety for downstream processing
    """
    print(f"[tool] get_weather('{city}')")
    weather_db = {
        "bengaluru": {"city": "Bengaluru", "temperature": 28.0, "condition": "Partly Cloudy", "humidity": 65},
        "delhi":     {"city": "Delhi",     "temperature": 35.0, "condition": "Sunny",          "humidity": 40},
        "mumbai":    {"city": "Mumbai",    "temperature": 32.0, "condition": "Humid",           "humidity": 80},
    }
    result = weather_db.get(city.lower())
    if result:
        return result
    return {"city": city, "error": "No weather data available"}


@mcp.tool()
def search_products(query: str, max_results: int = 5) -> list[dict]:
    """
    Search product catalog and return structured results.

    Args:
        query: Search term.
        max_results: Maximum number of results to return.
    """
    print(f"[tool] search_products('{query}', max={max_results})")
    all_products = [
        {"id": "P001", "name": "Mechanical Keyboard", "price": 4999, "in_stock": True},
        {"id": "P002", "name": "USB-C Hub",            "price": 2499, "in_stock": True},
        {"id": "P003", "name": "Webcam HD",            "price": 3999, "in_stock": False},
        {"id": "P004", "name": "Monitor Stand",        "price": 1999, "in_stock": True},
        {"id": "P005", "name": "Mouse Pad XL",         "price": 999,  "in_stock": True},
    ]
    matches = [
        p for p in all_products
        if query.lower() in p["name"].lower()
    ]
    return matches[:max_results]


# ============================================================
# PART 5: Stateless HTTP mode (for horizontal scaling)
# ============================================================

# stateless_http=True (already set above) means:
#
# STATEFUL (default):
#   - Server maintains a session per client connection
#   - Clients get a consistent server instance
#   - NOT safe for multiple replicas behind a load balancer
#     (each request might hit a different replica with no shared state)
#
# STATELESS:
#   - Each HTTP request is handled independently
#   - No session state is stored between requests
#   - SAFE for horizontal scaling — any replica can handle any request
#   - Required for: Docker Swarm, Kubernetes, Cloud Run, Lambda
#
# The tradeoff: stateless servers can't do server-to-client notifications
# (the server can't push updates between requests). For most tool use cases,
# this is fine — tools are request/response, not streaming.

@mcp.tool()
def ping() -> str:
    """Health check — works in stateless mode."""
    print("[tool] ping()")
    return "pong"


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "streamable-http"

    print(f"\nStarting advanced server on port 8002 ({transport})")
    print("Endpoint: http://localhost:8002/mcp")
    print("Features: lifespan, progress, structured output, stateless HTTP")

    mcp.run(transport=transport, host="0.0.0.0", port=8002)


# ============================================
# WHAT JUST HAPPENED:
#   LIFESPAN: db_pool and http_client are created ONCE on startup,
#   injected into every tool via ctx.request_context.lifespan_context.
#
#   PROGRESS: ctx.report_progress(current, total) sends progress to client.
#   ctx.info(msg) sends log messages. Both visible in MCP Inspector.
#
#   STRUCTURED OUTPUT: Returning dict/list instead of str gives clients
#   richer, typed data with an auto-generated JSON schema.
#
#   STATELESS: stateless_http=True allows multiple server replicas.
#   Each request is independent — safe for load balancers.
#
# WHEN TO USE EACH:
#   Lifespan  → DB connections, ML models, HTTP clients (always use for these)
#   Progress  → Any operation taking >1s (file processing, batch jobs)
#   Structured → When callers need to parse the response programmatically
#   Stateless  → Production deployments with auto-scaling
#
# EXERCISE 1:
# Add a tool that uses the http_client from AppContext:
#   @mcp.tool()
#   async def get_user(user_id: str, ctx: Context) -> dict:
#       client = ctx.request_context.lifespan_context.http_client
#       # Simulate: return await client.get(f"/users/{user_id}")
#       return {"id": user_id, "name": "Demo User"}
#
# EXERCISE 2:
# Add a progress-reporting tool that processes a list of IDs:
#   @mcp.tool()
#   async def batch_process(ids: list[int], ctx: Context) -> str:
#       for i, id in enumerate(ids):
#           await ctx.report_progress(i, len(ids))
#           await asyncio.sleep(0.1)
#       return f"Processed {len(ids)} IDs"
#
# EXERCISE 3:
# Change stateless_http=True to False. What behavior changes?
# Try connecting two clients simultaneously and observe session handling.
# ============================================
