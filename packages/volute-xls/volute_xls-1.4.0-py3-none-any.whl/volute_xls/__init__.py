"""
Volute-XLS - Excel Integration for AI Applications

A Model Context Protocol (MCP) server that enables AI agents to interact with
Microsoft Excel spreadsheets and local files on Windows machines.

Features:
- Excel COM automation via xlwings
- Comprehensive metadata extraction
- Sheet image capture for multimodal analysis
- Local file system access
- Thread-safe Excel operations
- FastMCP-based implementation

Example Usage:
    # Install via pip
    pip install volute-xls
    
    # Run local server for Excel integration
    volute-xls-local
    
    # Use in MCP configuration
    {
        "volute-xls-local": {
            "command": "volute-xls-local",
            "args": ["--transport", "stdio"],
            "env": {}
        }
    }
"""

__version__ = "1.4.0"
__author__ = "Coritan"
__email__ = "your-email@example.com"
__description__ = "MCP server for Excel integration in AI applications"

from .server import main as server_main
from .server_local import main as local_main
from .sdk import VoluteXLSClient, VoluteXLSError, create_client

__all__ = [
    "server_main", 
    "local_main", 
    "VoluteXLSClient", 
    "VoluteXLSError", 
    "create_client"
]
