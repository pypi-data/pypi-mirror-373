from smolagents import ToolCollection
from mcp import StdioServerParameters
from dotenv import dotenv_values
import sys

env_vars = dotenv_values(".env")

async def init_agent_tools():
    # Firebase MCP setup
    firebase_server = {
        "command": "npx",
        "args": ["-y", "firebase-tools", "experimental:mcp", "--dir", "."] 
    }
    
    return firebase_server