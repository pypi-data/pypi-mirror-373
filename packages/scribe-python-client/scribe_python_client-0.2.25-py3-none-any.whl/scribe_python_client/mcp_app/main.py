#This is Used for Running Locally
from .endpointsAPI import app
from fastapi_mcp import FastApiMCP
from pathlib import Path
import json


def run_mcp_server():
    mcp = FastApiMCP(
        app,
        name="MCPEndpoints",
        description="Tools for querying data from Scribe database using FastAPI endpoints with MCP",
    )

    mcp.mount()
    mcp.setup_server()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
