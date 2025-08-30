#!/usr/bin/env python3
"""
Excel Operations MCP Tools Registration

This module registers the Excel operations MCP tools for use with the MCP framework.
"""

import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

def register_excel_mcp_tools(mcp):
    """
    Register Excel operations MCP tools with the FastMCP framework.
    
    Args:
        mcp: FastMCP instance to register tools with
    """
    from fastmcp import FastMCP
    from pydantic import Field
    
    try:
        # Import both old and optimized versions
        from .excel_operations_tools import (
            excel_cell_operations,
            excel_row_column_operations, 
            excel_sheet_operations
        )
        
        from .excel_operations_optimized import (
            excel_edit,
            excel_quick_cells,
            excel_quick_format
        )
        
        from .excel_export_tools import excel_export_to_pdf
        
        # Import chart tools
        from .tools.charts.excel_chart_tools import (
            create_excel_chart,
            style_excel_chart,
            update_chart_data
        )
        
        # Register the ultra-simple main tool - BEST FOR AI AGENTS
        @mcp.tool()
        def excel_edit_natural(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            commands: str = Field(description="Natural commands (one per line): A1 = \"Hello\", B1 = 42, A1 bold, insert row 5, add sheet \"Data\""),
            sheet: str = Field(default=None, description="Optional sheet name (auto-detected if not provided)")
        ) -> str:
            """EASIEST Excel editing tool for AI agents! Use natural commands like: A1 = \"Hello\", B1 = 42, A1 bold, insert row 5, add sheet \"Data\"."""
            # Convert sheet parameter to proper string if it's not None
            sheet_name = None if sheet is None else str(sheet) if not isinstance(sheet, str) else sheet
            return excel_edit(excel_path, commands, sheet_name)
        
        # Register quick cell operations - SIMPLEST FOR CELL VALUES
        @mcp.tool()
        def excel_set_cells(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            cell_data: str = Field(description="Cell assignments (one per line): A1 = \"Text\", B1 = 123, C1 = =SUM(A1:B1)"),
            sheet: str = Field(default=None, description="Sheet name (optional)")
        ) -> str:
            """Set cell values with the simplest possible syntax: A1 = \"Text\", B1 = 123, C1 = =SUM(A1:B1)."""
            # Convert sheet parameter to proper string if it's not None
            sheet_name = None if sheet is None else str(sheet) if not isinstance(sheet, str) else sheet
            return excel_quick_cells(excel_path, cell_data, sheet_name)
        
        # Register quick formatting - SIMPLEST FOR FORMATTING
        @mcp.tool()
        def excel_format_cells(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            format_commands: str = Field(description="Format commands (one per line): A1 bold, B1 background yellow, C1 font red"),
            sheet: str = Field(default=None, description="Sheet name (optional)")
        ) -> str:
            """Format cells with simple commands: A1 bold, B1 background yellow, C1 font red."""
            # Convert sheet parameter to proper string if it's not None
            sheet_name = None if sheet is None else str(sheet) if not isinstance(sheet, str) else sheet
            return excel_quick_format(excel_path, format_commands, sheet_name)
        
        # Register Excel export tool with print layout settings
        @mcp.tool()
        def excel_export(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            output_path: str = Field(default=None, description="Path for the output PDF (default: same as Excel with .pdf)"),
            print_settings: dict = Field(default=None, description="Dictionary of print settings (orientation, margins, etc.)"),
            sheets: list = Field(default=None, description="List of sheet names to include (default: all sheets)"),
            overwrite: bool = Field(default=False, description="Whether to overwrite existing PDF file")
        ) -> str:
            """Export Excel file to PDF with print layout settings. Configures page setup and exports to PDF.
            
            Print Settings Options:
            - orientation: "portrait" or "landscape"
            - paper_size: "letter", "a4", etc.
            - fit_to_pages: [width, height] e.g. [1, 0] for fit to 1 page wide
            - margins: [left, right, top, bottom] in inches
            - center_horizontal: True/False
            - center_vertical: True/False
            - print_gridlines: True/False
            - print_titles: True/False
            - header: {"left": "text", "center": "text", "right": "text"}
            - footer: {"left": "text", "center": "text", "right": "text"}
            """
            return excel_export_to_pdf(
                excel_path=excel_path,
                output_path=output_path,
                print_settings=print_settings,
                sheets=sheets,
                overwrite=overwrite
            )
        
        # Keep original tools for backwards compatibility
        @mcp.tool()
        def excel_dsl_cells(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            cell_operations: str = Field(description="DSL string specifying cell operations (formatting, values, formulas)")
        ) -> str:
            """Perform cell operations on an Excel file using DSL format. Set cell values, format cells, and add data validation."""
            return excel_cell_operations(excel_path, cell_operations)
        
        @mcp.tool()
        def excel_dsl_rows_columns(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            row_column_operations: str = Field(description="DSL string specifying row/column operations")
        ) -> str:
            """Perform row and column operations on an Excel file using DSL format. Insert/delete/resize/hide rows and columns."""
            return excel_row_column_operations(excel_path, row_column_operations)
        
        @mcp.tool()
        def excel_dsl_sheets(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            sheet_operations: str = Field(description="DSL string specifying sheet operations")
        ) -> str:
            """Perform sheet operations on an Excel file using DSL format. Add/delete/rename/move/copy worksheets."""
            return excel_sheet_operations(excel_path, sheet_operations)
        
        # Register Chart Tools
        @mcp.tool()
        def excel_create_chart(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            chart_name: str = Field(description="Unique name for the chart (e.g., 'sales_chart', 'monthly_trends')"),
            chart_type: str = Field(description="Chart type: line, column_clustered, bar_clustered, pie, xy_scatter, area, 3d_column, bubble, doughnut, radar"),
            x_axis_range: str = Field(description="Cell range for X-axis data (e.g., 'A1:A10', 'B2:B13')"),
            data_series: str = Field(description="Data series format: 'series_1=B1:B10' or 'series_1=B1:B10,series_2=C1:C10,series_3=D1:D10'"),
            sheet_name: str = Field(default=None, description="Sheet name (optional, uses first sheet if not specified)")
        ) -> str:
            """Create a new Excel chart with data series. Perfect for AI agents to quickly generate charts from Excel data.
            
            Examples:
            - Simple line chart: chart_type='line', x_axis_range='A2:A13', data_series='series_1=B2:B13'
            - Multi-series column: chart_type='column_clustered', x_axis_range='A1:A4', data_series='series_1=B1:B4,series_2=C1:C4'
            - Pie chart: chart_type='pie', x_axis_range='A1:A5', data_series='series_1=B1:B5'
            
            Supported chart types: line, line_markers, column_clustered, bar_clustered, pie, xy_scatter,
            area, area_stacked, 3d_column, 3d_pie, bubble, doughnut, radar
            """
            return create_excel_chart(
                excel_path=excel_path,
                chart_name=chart_name,
                chart_type=chart_type,
                x_axis_range=x_axis_range,
                data_series=data_series,
                sheet_name=sheet_name
            )
        
        @mcp.tool()
        def excel_style_chart(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            chart_name: str = Field(description="Name of the chart to style (must match existing chart name)"),
            formatting_properties: str = Field(description="Chart styling properties using pipe-separated format"),
            sheet_name: str = Field(default=None, description="Sheet name (optional)")
        ) -> str:
            """Style an existing Excel chart with advanced formatting options. Control titles, axes, colors, grids, and areas.
            
            Formatting Properties Syntax (pipe-separated):
            title="Chart Title"|title_pos="above"|title_font=[Arial,14,true,false,#000000]|
            legend="true"|legend_pos="bottom"|
            x_title="X Axis"|x_title_font=[Arial,10,false,false,#666666]|x_grid="true"|x_grid_color="#E0E0E0"|
            y_title="Y Axis"|y_title_font=[Arial,10,false,false,#666666]|y_grid="true"|y_grid_color="#E0E0E0"|
            s1_color="#FF0000"|s2_color="#00FF00"|s3_color="#0000FF"|
            plot_fill="#FAFAFA"|plot_border="true"|plot_border_color="#CCCCCC"|
            chart_fill="#FFFFFF"|chart_border="true"|chart_border_color="#333333"
            
            Examples:
            - Basic styling: "title=Sales Report|s1_color=#FF6B6B|legend=true"
            - Advanced axes: "x_title=Month|y_title=Revenue|x_grid=true|y_grid=true|plot_fill=#F8F8F8"
            """
            return style_excel_chart(
                excel_path=excel_path,
                chart_name=chart_name,
                formatting_properties=formatting_properties,
                sheet_name=sheet_name
            )
        
        @mcp.tool()
        def excel_update_chart_data(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            chart_name: str = Field(description="Name of the chart to update (must match existing chart name)"),
            x_axis_range: str = Field(default=None, description="New X-axis data range (e.g., 'A1:A12', optional)"),
            data_series: str = Field(default=None, description="New data series: 'series_1=B1:B12,series_2=C1:C12' (optional)"),
            series_names: str = Field(default=None, description="Series name mappings: 'series_1=B1,series_2=C1' (optional)"),
            sheet_name: str = Field(default=None, description="Sheet name (optional)")
        ) -> str:
            """Update data ranges and series names for an existing Excel chart. Perfect for dynamic data updates.
            
            Examples:
            - Update ranges: x_axis_range='A1:A24', data_series='series_1=B1:B24,series_2=C1:C24'
            - Update names only: series_names='series_1=B1,series_2=C1'
            - Add new series: data_series='series_1=B2:B13,series_2=C2:C13,series_3=D2:D13'
            
            At least one of x_axis_range, data_series, or series_names must be provided.
            """
            return update_chart_data(
                excel_path=excel_path,
                chart_name=chart_name,
                x_axis_range=x_axis_range,
                data_series=data_series,
                series_names=series_names,
                sheet_name=sheet_name
            )
        
        logger.info("Successfully registered Excel operations MCP tools (including chart tools and optimized AI-friendly tools)")
        
    except Exception as e:
        logger.error(f"Failed to register Excel operations MCP tools: {e}")
        raise


if __name__ == "__main__":
    # Example registration (for testing)
    def mock_register(name, description, input_schema, func):
        print(f"Registered tool: {name}")
        print(f"Description: {description}")
        print(f"Schema: {input_schema}")
        print("-" * 50)
    
    register_excel_mcp_tools(mock_register)
