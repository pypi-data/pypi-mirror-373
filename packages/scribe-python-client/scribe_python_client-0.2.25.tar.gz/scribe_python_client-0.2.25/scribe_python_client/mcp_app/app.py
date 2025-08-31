#This is used for hosting on HuggingFace
from fastapi_mcp import FastApiMCP
from .endpointsAPI import app

mcp = FastApiMCP(
    app,
    name="MCPEndpoints",
    description="Tools for querying data from Scribe database using FastAPI endpoints with MCP",
)

mcp.mount()
mcp.setup_server()
