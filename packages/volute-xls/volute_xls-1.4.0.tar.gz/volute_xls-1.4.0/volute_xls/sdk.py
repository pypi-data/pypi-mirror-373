"""
Volute-XLS SDK - Client library for connecting to Volute-XLS MCP servers.

This SDK provides a convenient Python interface for connecting to both local
and cloud Volute-XLS servers and calling Excel analysis tools programmatically.
"""

import httpx
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VoluteXLSError(Exception):
    """Custom exception for Volute-XLS client errors."""
    pass


@dataclass
class ServerInfo:
    """Information about a Volute-XLS server."""
    name: str
    type: str  # "LOCAL" or "CLOUD"
    host: str
    port: int
    status: str
    excel_available: bool = False
    xlwings_available: bool = False
    openpyxl_available: bool = False


class VoluteXLSClient:
    """
    Base client for Volute-XLS MCP servers.
    
    Provides methods to connect to and interact with both local and cloud
    Excel analysis servers.
    """
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the MCP server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = httpx.AsyncClient(timeout=timeout)
        self._server_info = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.aclose()
    
    async def get_server_info(self) -> ServerInfo:
        """Get information about the server."""
        try:
            response = await self.session.get(f"{self.base_url}/info")
            info_text = response.text
            
            # Parse basic server info from text response
            lines = info_text.split('\\n')
            info_dict = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    info_dict[key.strip()] = value.strip()
            
            self._server_info = ServerInfo(
                name=info_dict.get('Server', 'Unknown'),
                type=info_dict.get('Type', 'Unknown'),
                host=self.base_url.split('://')[1].split(':')[0] if '://' in self.base_url else 'localhost',
                port=int(self.base_url.split(':')[-1]) if ':' in self.base_url.split('/')[-1] else 80,
                status=info_dict.get('Status', 'Unknown')
            )
            
            return self._server_info
            
        except Exception as e:
            logger.error(f"Failed to get server info: {e}")
            raise VoluteXLSError(f"Could not retrieve server information: {e}")
    
    async def health_check(self) -> bool:
        """Check if the server is healthy."""
        try:
            response = await self.session.get(f"{self.base_url}/health")
            return response.status_code == 200 and "OK" in response.text
        except Exception:
            return False
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool arguments
            
        Returns:
            Tool response data
        """
        try:
            payload = {
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": kwargs
                }
            }
            
            response = await self.session.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise VoluteXLSError(f"Server returned status {response.status_code}: {response.text}")
            
            result = response.json()
            
            if "error" in result:
                raise VoluteXLSError(f"Tool error: {result['error']}")
            
            return result.get("result", {})
            
        except httpx.RequestError as e:
            raise VoluteXLSError(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            raise VoluteXLSError(f"Invalid JSON response: {e}")
    
    # Convenience methods for Excel tools
    
    async def extract_excel_metadata(self, excel_path: str, 
                                   include_sheet_content: bool = True,
                                   include_sheet_data: bool = False,
                                   output_format: str = "json") -> Dict[str, Any]:
        """
        Extract metadata from an Excel file.
        
        Args:
            excel_path: Path to Excel file
            include_sheet_content: Include detailed sheet analysis
            include_sheet_data: Include sample cell data
            output_format: Output format ("json" or "summary")
            
        Returns:
            Excel metadata
        """
        return await self.call_tool(
            "extract_excel_metadata",
            excel_path=excel_path,
            include_sheet_content=include_sheet_content,
            include_sheet_data=include_sheet_data,
            output_format=output_format
        )
    
    async def analyze_excel_sheets(self, excel_path: str,
                                 sheet_names: Optional[List[str]] = None,
                                 include_data_sample: bool = True,
                                 max_rows: int = 50,
                                 include_formatting: bool = False) -> Dict[str, Any]:
        """
        Analyze specific sheets in an Excel file.
        
        Args:
            excel_path: Path to Excel file
            sheet_names: List of sheet names to analyze (None for all)
            include_data_sample: Include sample data
            max_rows: Maximum rows to include in sample
            include_formatting: Include cell formatting
            
        Returns:
            Sheet analysis results
        """
        return await self.call_tool(
            "analyze_excel_sheets",
            excel_path=excel_path,
            sheet_names=sheet_names,
            include_data_sample=include_data_sample,
            max_rows=max_rows,
            include_formatting=include_formatting
        )
    
    async def capture_excel_sheets(self, excel_path: str,
                                 sheet_names: List[str],
                                 image_width: int = 1200,
                                 image_height: int = 800,
                                 include_metadata: bool = True,
                                 zoom_level: float = 100.0) -> Dict[str, Any]:
        """
        Capture Excel sheets as images.
        
        Args:
            excel_path: Path to Excel file
            sheet_names: List of sheet names to capture
            image_width: Image width in pixels
            image_height: Image height in pixels
            include_metadata: Include capture metadata
            zoom_level: Zoom level percentage
            
        Returns:
            Image capture results
        """
        return await self.call_tool(
            "capture_excel_sheets",
            excel_path=excel_path,
            sheet_names=sheet_names,
            image_width=image_width,
            image_height=image_height,
            include_metadata=include_metadata,
            zoom_level=zoom_level
        )
    
    async def capture_excel_ranges(self, excel_path: str,
                                 sheet_ranges: Dict[str, List[str]],
                                 image_width: int = 800,
                                 image_height: int = 600,
                                 include_metadata: bool = True,
                                 zoom_level: float = 100.0) -> Dict[str, Any]:
        """
        Capture specific Excel ranges as images.
        
        Args:
            excel_path: Path to Excel file
            sheet_ranges: Dictionary mapping sheet names to range lists
            image_width: Image width in pixels
            image_height: Image height in pixels
            include_metadata: Include capture metadata
            zoom_level: Zoom level percentage
            
        Returns:
            Range capture results
        """
        return await self.call_tool(
            "capture_excel_ranges",
            excel_path=excel_path,
            sheet_ranges=sheet_ranges,
            image_width=image_width,
            image_height=image_height,
            include_metadata=include_metadata,
            zoom_level=zoom_level
        )
    
    async def get_excel_capabilities(self) -> Dict[str, Any]:
        """Get Excel analysis capabilities of the server."""
        return await self.call_tool("get_excel_capabilities")
    
    async def list_local_files(self, directory: str = ".", pattern: str = "*.xlsx") -> List[Dict[str, Any]]:
        """List Excel files in a local directory."""
        return await self.call_tool(
            "list_local_files",
            directory=directory,
            pattern=pattern
        )


class VoluteXLSLocalClient(VoluteXLSClient):
    """Client for local Volute-XLS servers."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8002, timeout: int = 30):
        """
        Initialize local client.
        
        Args:
            host: Server host
            port: Server port  
            timeout: Request timeout in seconds
        """
        super().__init__(f"http://{host}:{port}", timeout)


class VoluteXLSCloudClient(VoluteXLSClient):
    """Client for cloud Volute-XLS servers."""
    
    def __init__(self, base_url: str, timeout: int = 60):
        """
        Initialize cloud client.
        
        Args:
            base_url: Cloud server base URL
            timeout: Request timeout in seconds (longer for cloud)
        """
        super().__init__(base_url, timeout)


def create_client(server_type: str = "local", **kwargs) -> VoluteXLSClient:
    """
    Create a Volute-XLS client.
    
    Args:
        server_type: "local" or "cloud"
        **kwargs: Additional arguments for client initialization
        
    Returns:
        Configured client instance
    """
    if server_type.lower() == "local":
        return VoluteXLSLocalClient(**kwargs)
    elif server_type.lower() == "cloud":
        return VoluteXLSCloudClient(**kwargs)
    else:
        raise VoluteXLSError(f"Unknown server type: {server_type}")


# Synchronous wrapper functions for convenience

def sync_extract_excel_metadata(excel_path: str, server_type: str = "local", **kwargs) -> Dict[str, Any]:
    """Synchronous wrapper for Excel metadata extraction."""
    async def _extract():
        async with create_client(server_type) as client:
            return await client.extract_excel_metadata(excel_path, **kwargs)
    
    return asyncio.run(_extract())


def sync_analyze_excel_sheets(excel_path: str, server_type: str = "local", **kwargs) -> Dict[str, Any]:
    """Synchronous wrapper for Excel sheet analysis."""
    async def _analyze():
        async with create_client(server_type) as client:
            return await client.analyze_excel_sheets(excel_path, **kwargs)
    
    return asyncio.run(_analyze())


def sync_capture_excel_sheets(excel_path: str, sheet_names: List[str], 
                            server_type: str = "local", **kwargs) -> Dict[str, Any]:
    """Synchronous wrapper for Excel sheet capture."""
    async def _capture():
        async with create_client(server_type) as client:
            return await client.capture_excel_sheets(excel_path, sheet_names, **kwargs)
    
    return asyncio.run(_capture())
