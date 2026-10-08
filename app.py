import contextlib
import os
from collections.abc import AsyncIterator

from fastapi import FastAPI

from mcp.server.transport_security import (
    TransportSecuritySettings,
)

from oauth_callback import router as oauth_router
from whoop_mcp.server import mcp


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PUBLIC_HOST = (
    os.getenv("PUBLIC_HOST")
    or "localhost"
).strip()


# --------------------------------------------------
# MCP transport security
# --------------------------------------------------

transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=[
        "127.0.0.1",
        "127.0.0.1:*",
        "localhost",
        "localhost:*",
        PUBLIC_HOST,
        f"{PUBLIC_HOST}:*",
    ],
    allowed_origins=[
        "http://127.0.0.1:*",
        "http://localhost:*",
        f"https://{PUBLIC_HOST}",
    ],
)


# --------------------------------------------------
# Build MCP Streamable HTTP application
# --------------------------------------------------
#
# We keep the MCP app's normal /mcp route and mount
# the MCP application at "/" below.
#
# Result:
#     https://your-domain/mcp
#
# This avoids accidentally creating /mcp/mcp.
# --------------------------------------------------

mcp_app = mcp.streamable_http_app(
    streamable_http_path="/mcp",
    json_response=True,
    stateless_http=True,
    transport_security=transport_security,
)


# --------------------------------------------------
# Application lifespan
# --------------------------------------------------
#
# Mounted ASGI applications do not automatically run
# the MCP sub-application's lifespan.
#
# Therefore the parent FastAPI application explicitly
# starts the MCP session manager.
# --------------------------------------------------

@contextlib.asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:

    async with mcp.session_manager.run():
        yield


# --------------------------------------------------
# Main FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Personal WHOOP MCP",
    description=(
        "A self-hosted MCP server that securely connects "
        "WHOOP health and fitness data with MCP-compatible "
        "AI applications."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# --------------------------------------------------
# OAuth / web routes
# --------------------------------------------------
#
# These provide:
#
# /
# /connect
# /callback
# /privacy
# --------------------------------------------------

app.include_router(
    oauth_router
)


# --------------------------------------------------
# MCP application
# --------------------------------------------------
#
# Mounting at "/" while the MCP application itself
# uses /mcp keeps the final endpoint exactly:
#
#     /mcp
#
# OAuth/FastAPI routes were registered first, so they
# continue to handle their specific paths.
# --------------------------------------------------

app.mount(
    "/",
    mcp_app,
)