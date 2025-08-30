"""
Volute-XLS Local Server - Excel-focused MCP server for local COM access.

This server runs locally on Windows machines with Excel installed,
providing COM-based Excel manipulation tools and multimodal sheet capture.

Run with: python server_local.py
"""

import os
import sys
import logging
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Server configuration
SERVER_NAME = os.getenv("LOCAL_SERVER_NAME", "Volute-XLS-Local")
SERVER_HOST = os.getenv("LOCAL_SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("LOCAL_SERVER_PORT", "8002"))

# Create FastMCP server instance
mcp = FastMCP(
    name=SERVER_NAME,
    instructions=f"""
        This is a LOCAL Volute-XLS server providing Excel analysis and multimodal tools.
        
        **Local Access Features**:
        - Excel COM integration via xlwings (comprehensive metadata extraction)
        - Sheet image capture for multimodal LLM analysis
        - Range-specific image capture for focused analysis
        - Local file system access
        - Windows-specific functionality
        - Thread-safe Excel operations
        
        **Multimodal Capabilities**:
        - Capture Excel sheets as images
        - Capture specific cell ranges as images
        - Export sheets for visual analysis by multimodal LLMs
        - Return base64-encoded images compatible with vision models
        - Support for selective sheet capture (specify sheet names)
        - Zoom control for optimal image quality
        
        **Excel Analysis Tools**:
        - Comprehensive workbook metadata extraction
        - Sheet structure and content analysis
        - Formula and data type detection
        - Charts and images detection
        - Named ranges and merged cells analysis
        - Sample data extraction for content understanding
        
        **Excel Operations Tools**:
        - excel_cell_operations_tool: Set cell values, formulas, formatting, data validation, conditional formatting
        - excel_row_column_operations_tool: Insert/delete/resize/hide rows and columns, format entire rows/columns
        - excel_sheet_operations_tool: Add/delete/rename/move/copy worksheets, set tab colors, protect sheets
        
        **Requirements**:
        - Windows operating system (required)
        - Microsoft Excel installed on user machine (required)
        - Local file access permissions
    """,
    on_duplicate_tools="warn",
    on_duplicate_resources="warn", 
    on_duplicate_prompts="replace",
    include_fastmcp_meta=True,
)

# ============================================================================
# EXCEL TOOLS REGISTRATION (LOCAL COM ACCESS)
# ============================================================================

try:
    # Import from the relative package module
    from .excel_tools import register_excel_tools
    register_excel_tools(mcp)
    logger.info("Excel metadata tools registered (local access)")
except ImportError as e:
    logger.warning(f"Excel tools not available: {e}")
except Exception as e:
    logger.error(f"Error registering Excel tools: {e}")

# ============================================================================
# SHEET IMAGE CAPTURE TOOLS (MULTIMODAL SUPPORT)
# ============================================================================

try:
    from .sheet_capture_tools import register_sheet_capture_tools
    register_sheet_capture_tools(mcp)
    logger.info("Sheet image capture tools registered (multimodal support)")
except ImportError as e:
    logger.warning(f"Sheet capture tools not available: {e}")
except Exception as e:
    logger.error(f"Error registering sheet capture tools: {e}")

# ============================================================================
# EXCEL OPERATIONS TOOLS (CELL, ROW/COLUMN, SHEET OPERATIONS)
# ============================================================================

try:
    from .excel_operations_mcp import register_excel_mcp_tools
    register_excel_mcp_tools(mcp)
    logger.info("Excel operations tools registered (cell, row/column, sheet operations)")
except ImportError as e:
    logger.warning(f"Excel operations tools not available: {e}")
except Exception as e:
    logger.error(f"Error registering Excel operations tools: {e}")

# ============================================================================
# EXCEL FILE CREATION TOOLS
# ============================================================================

try:
    from .excel_creation_tools import create_excel_file as create_excel_file_func, create_excel_from_template as create_excel_from_template_func
    
    @mcp.tool(tags={"excel", "create", "local"})
    def create_excel(
        excel_path: str,
        initial_data: str = "",
        sheets: list = None,
        overwrite: bool = False
    ) -> str:
        """
        Create a new Excel file at the specified path with optional initial data.
        
        This tool allows you to create Excel files from scratch at any file path,
        with optional initial content and formatting using natural language commands.
        
        Args:
            excel_path: Full path where the Excel file should be created
            initial_data: Optional natural language commands to populate the file
                         (e.g., 'A1 = "Title"\nA1 bold\nB2 = 123')
            sheets: List of sheet names to create (default: ['Sheet1'])
            overwrite: Whether to overwrite existing files (default: False)
            
        Returns:
            JSON string with creation result and file information
            
        Examples:
            # Create empty file
            create_excel("C:/reports/monthly.xlsx")
            
            # Create with data
            create_excel(
                "C:/data/sales.xlsx", 
                "A1 = 'Sales Report'\nA1 bold\nA1 fill #0000FF\nA3 = 'Q1 Data'"
            )
            
            # Create with multiple sheets
            create_excel(
                "C:/analysis/workbook.xlsx", 
                sheets=["Summary", "Data", "Charts"]
            )
        """
        return create_excel_file_func(excel_path, initial_data, sheets, overwrite)
    
    logger.info("Excel file creation tools registered")
except ImportError as e:
    logger.warning(f"Excel creation tools not available: {e}")
except Exception as e:
    logger.error(f"Error registering Excel creation tools: {e}")

# ============================================================================
# LOCAL RESOURCES - Local data sources
# ============================================================================

@mcp.resource("local://system")
def get_local_system_status() -> dict:
    """Provides local system status and capabilities."""
    return {
        "server_type": "LOCAL",
        "excel_integration": True,
        "local_file_access": True,
        "com_objects": True,
        "multimodal_capture": True,
        "companion_cloud_server": "https://volutemcp-server.onrender.com"
    }

@mcp.resource("local://files/{directory}")
def get_directory_listing(directory: str) -> dict:
    """Get listing of files in a local directory."""
    import os
    import glob
    
    if not os.path.exists(directory):
        return {"error": f"Directory not found: {directory}"}
    
    files = []
    for file_path in glob.glob(os.path.join(directory, "*")):
        if os.path.isfile(file_path):
            files.append({
                "name": os.path.basename(file_path),
                "path": file_path,
                "size": os.path.getsize(file_path),
                "extension": os.path.splitext(file_path)[1],
                "is_excel": os.path.splitext(file_path)[1].lower() in ['.xlsx', '.xlsm', '.xls']
            })
    
    return {
        "directory": directory,
        "files": files,
        "count": len(files),
        "excel_files": len([f for f in files if f["is_excel"]])
    }

# ============================================================================
# CUSTOM ROUTES
# ============================================================================

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint."""
    return PlainTextResponse("LOCAL-OK")

@mcp.custom_route("/info", methods=["GET"])
async def server_info_endpoint(request: Request) -> PlainTextResponse:
    """Local server information endpoint."""
    info = f"Server: {SERVER_NAME}\\nType: LOCAL\\nExcel: Available\\nStatus: Running"
    return PlainTextResponse(info)

# ============================================================================
# SERVER STARTUP
# ============================================================================

def main():
    """Main entry point for the local server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Volute-XLS Local Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "http"], 
        default="http",
        help="Transport protocol (default: http)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=SERVER_PORT,
        help=f"Port number for HTTP transport (default: {SERVER_PORT})"
    )
    parser.add_argument(
        "--host", 
        default=SERVER_HOST,
        help=f"Host address for HTTP transport (default: {SERVER_HOST})"
    )
    
    # Support legacy stdio argument
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        args = argparse.Namespace(transport="stdio", port=SERVER_PORT, host=SERVER_HOST)
    else:
        args = parser.parse_args()
    
    if args.transport == "stdio":
        # STDIO transport for local MCP clients
        logger.info(f"Starting {SERVER_NAME} with STDIO transport...")
        mcp.run(transport="stdio")
    else:
        # HTTP transport
        logger.info(f"Starting {SERVER_NAME} LOCAL server...")
        logger.info(f"Local server: http://{args.host}:{args.port}")
        logger.info(f"Cloud companion: https://volutemcp-server.onrender.com")
        logger.info(f"Health check: http://{args.host}:{args.port}/health")
        mcp.run(
            transport="http",
            host=args.host,
            port=args.port,
        )

if __name__ == "__main__":
    main()
