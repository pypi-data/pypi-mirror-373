"""
Advanced Excel tools for FastMCP server.
Provides comprehensive Excel manipulation capabilities including metadata extraction,
workbook analysis, sheet content analysis, and more.
"""

import os
import json
import tempfile
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Import our Excel metadata extractor
from .excel_metadata import ExcelMetadataExtractor, OPENPYXL_AVAILABLE, XLWINGS_AVAILABLE

# Configure logging
logger = logging.getLogger(__name__)


class ExcelAnalysisResult(BaseModel):
    """Model for Excel analysis results."""
    success: bool = Field(description="Whether the analysis was successful")
    message: str = Field(description="Status message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Analysis data")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class SheetContentSummary(BaseModel):
    """Model for sheet content summary."""
    sheet_name: str = Field(description="Sheet name")
    sheet_index: int = Field(description="Sheet index (0-based)")
    used_range: str = Field(description="Used range address (e.g., A1:D10)")
    total_rows: int = Field(description="Total rows with data")
    total_columns: int = Field(description="Total columns with data")
    cell_count: int = Field(description="Total non-empty cells")
    formula_count: int = Field(description="Total formula cells")
    has_charts: bool = Field(description="Whether sheet contains charts")
    has_images: bool = Field(description="Whether sheet contains images")
    merged_cells_count: int = Field(description="Number of merged cell ranges")


class WorkbookSummary(BaseModel):
    """Model for workbook summary."""
    filename: str = Field(description="Excel filename")
    total_sheets: int = Field(description="Total number of sheets")
    file_size: int = Field(description="File size in bytes")
    created: Optional[str] = Field(default=None, description="Creation date")
    modified: Optional[str] = Field(default=None, description="Last modified date")
    creator: Optional[str] = Field(default=None, description="File creator")
    sheets: List[SheetContentSummary] = Field(description="Summary of each sheet")


def register_excel_tools(mcp: FastMCP) -> None:
    """
    Register all Excel tools with the FastMCP server.
    
    Args:
        mcp: FastMCP instance to register tools with
    """
    
    @mcp.tool()
    def extract_excel_metadata(
        excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
        include_sheet_content: bool = Field(default=True, description="Include detailed sheet content analysis"),
        include_sheet_data: bool = Field(default=False, description="Include sample cell data (limited to first 100 rows)"),
        output_format: str = Field(default="json", description="Output format: 'json' or 'summary'")
    ) -> ExcelAnalysisResult:
        """
        Extract comprehensive metadata from an Excel workbook.
        
        This tool analyzes Excel files and extracts detailed information including:
        - Core properties (title, creator, creation date, etc.)
        - Workbook structure (sheet names, counts, etc.)
        - Sheet dimensions and used ranges
        - Cell content summary (formulas, values, empty cells)
        - Named ranges and workbook-level elements
        - Charts and images detection
        - Merged cells information
        - Optional sample data extraction
        """
        try:
            # Validate inputs
            if not excel_path or not excel_path.strip():
                return ExcelAnalysisResult(
                    success=False,
                    message="Error",
                    error="Excel file path is required and cannot be empty"
                )
            
            if not OPENPYXL_AVAILABLE:
                return ExcelAnalysisResult(
                    success=False,
                    message="Error",
                    error="openpyxl library is not available. Please install it with: pip install openpyxl"
                )
            
            # Validate file exists and is accessible
            try:
                excel_path = os.path.abspath(excel_path)
                if not os.path.exists(excel_path):
                    return ExcelAnalysisResult(
                        success=False,
                        message="Error",
                        error=f"File not found: {excel_path}"
                    )
                
                if not os.path.isfile(excel_path):
                    return ExcelAnalysisResult(
                        success=False,
                        message="Error",
                        error=f"Path is not a file: {excel_path}"
                    )
                
                # Check file permissions
                if not os.access(excel_path, os.R_OK):
                    return ExcelAnalysisResult(
                        success=False,
                        message="Error",
                        error=f"File is not readable: {excel_path}"
                    )
            except (OSError, IOError) as e:
                return ExcelAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"File access error: {str(e)}"
                )
            
            # Check file extension
            try:
                file_ext = os.path.splitext(excel_path)[1].lower()
                if file_ext not in ['.xlsx', '.xlsm', '.xls']:
                    return ExcelAnalysisResult(
                        success=False,
                        message="Error",
                        error=f"Unsupported file format: {file_ext}. Only .xlsx, .xlsm, and .xls files are supported."
                    )
            except Exception as e:
                return ExcelAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"Error checking file extension: {str(e)}"
                )
            
            # Extract metadata using our extractor with comprehensive error handling
            try:
                with ExcelMetadataExtractor(excel_path) as extractor:
                    if not extractor.workbook:
                        return ExcelAnalysisResult(
                            success=False,
                            message="Error",
                            error="Failed to open Excel workbook. The file may be corrupted or password-protected."
                        )
                    
                    metadata = extractor.extract_presentation_metadata(
                        include_sheet_content=include_sheet_content,
                        include_sheet_data=include_sheet_data,
                        max_data_rows=100 if include_sheet_data else None
                    )
            except PermissionError:
                return ExcelAnalysisResult(
                    success=False,
                    message="Error",
                    error="Permission denied accessing the Excel file. The file may be open in Excel or protected."
                )
            except FileNotFoundError:
                return ExcelAnalysisResult(
                    success=False,
                    message="Error",
                    error="Excel file was not found or has been moved/deleted."
                )
            except Exception as extraction_error:
                logger.error(f"Extraction error for {excel_path}: {str(extraction_error)}")
                return ExcelAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"Failed to extract Excel metadata: {str(extraction_error)}"
                )
            
            if output_format.lower() == "summary":
                # Convert to summary format
                summary = _create_workbook_summary(metadata)
                return ExcelAnalysisResult(
                    success=True,
                    message="Excel metadata extracted successfully (summary format)",
                    data=summary.dict()
                )
            else:
                return ExcelAnalysisResult(
                    success=True,
                    message="Excel metadata extracted successfully",
                    data=metadata
                )
                
        except Exception as e:
            logger.exception(f"Error extracting Excel metadata: {str(e)}")
            return ExcelAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"Failed to extract metadata: {str(e)}"
            )

    @mcp.tool()
    def analyze_excel_sheets(
        excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
        sheet_names: Optional[List[str]] = Field(default=None, description="Specific sheet names to analyze. If None, analyzes all sheets"),
        include_data_sample: bool = Field(default=True, description="Include sample data from each sheet"),
        max_rows: int = Field(default=50, description="Maximum rows of sample data to extract per sheet"),
        include_formatting: bool = Field(default=False, description="Include cell formatting information (slower)")
    ) -> ExcelAnalysisResult:
        """
        Analyze detailed content of specific sheets in an Excel workbook.
        
        This tool provides focused analysis of Excel worksheets, extracting:
        - Sheet structure and dimensions
        - Cell data and formulas
        - Data types and formatting
        - Charts and objects summary
        - Named ranges within sheets
        - Sample data for content understanding
        """
        try:
            if not OPENPYXL_AVAILABLE:
                return ExcelAnalysisResult(
                    success=False,
                    message="Error",
                    error="openpyxl library is not available. Please install it with: pip install openpyxl"
                )
            
            if not os.path.exists(excel_path):
                return ExcelAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"File not found: {excel_path}"
                )
            
            with ExcelMetadataExtractor() as extractor:
                extractor.open_workbook(excel_path)
                
                # Get basic workbook info
                metadata = extractor.extract_workbook_metadata(include_sheet_details=False)
                
                # Filter sheets if specified
                available_sheets = metadata.get("sheetNames", [])
                if sheet_names:
                    # Validate requested sheets exist
                    invalid_sheets = [s for s in sheet_names if s not in available_sheets]
                    if invalid_sheets:
                        return ExcelAnalysisResult(
                            success=False,
                            message="Error",
                            error=f"Sheet(s) not found: {', '.join(invalid_sheets)}. Available sheets: {', '.join(available_sheets)}"
                        )
                    sheets_to_analyze = sheet_names
                else:
                    sheets_to_analyze = available_sheets
                
                # Analyze each requested sheet
                sheet_analyses = []
                for sheet_name in sheets_to_analyze:
                    try:
                        # Get sheet metadata
                        sheet_metadata = extractor.extract_sheet_metadata(sheet_name)
                        
                        # Get sheet data if requested
                        if include_data_sample:
                            sheet_data = extractor.extract_sheet_data(
                                sheet_name,
                                max_rows=max_rows,
                                include_formatting=include_formatting
                            )
                            sheet_metadata["sampleData"] = sheet_data
                        
                        sheet_analyses.append(sheet_metadata)
                        
                    except Exception as e:
                        logger.error(f"Failed to analyze sheet {sheet_name}: {e}")
                        sheet_analyses.append({
                            "sheetName": sheet_name,
                            "error": str(e)
                        })
                
                result_data = {
                    "workbookInfo": {
                        "fileName": metadata["fileMetadata"]["fileName"],
                        "filePath": metadata["fileMetadata"]["filePath"],
                        "totalSheets": metadata["totalSheets"],
                        "analyzedSheets": len(sheet_analyses)
                    },
                    "sheets": sheet_analyses,
                    "analysisSettings": {
                        "includedDataSample": include_data_sample,
                        "maxRowsPerSheet": max_rows if include_data_sample else 0,
                        "includedFormatting": include_formatting
                    }
                }
            
            return ExcelAnalysisResult(
                success=True,
                message=f"Analyzed {len(sheet_analyses)} sheet(s) successfully",
                data=result_data
            )
                
        except Exception as e:
            logger.exception(f"Error analyzing Excel sheets: {str(e)}")
            return ExcelAnalysisResult(
                success=False,
                message="Error",
                error=f"Failed to analyze sheets: {str(e)}"
            )
    
    @mcp.tool()
    def get_excel_capabilities() -> Dict[str, Any]:
        """
        Get information about Excel analysis capabilities and requirements.
        
        Returns system capabilities for Excel file analysis.
        """
        try:
            capabilities = {
                "libraries_available": {
                    "openpyxl": OPENPYXL_AVAILABLE,
                    "xlwings": XLWINGS_AVAILABLE
                },
                "supported_formats": [".xlsx", ".xlsm", ".xls"],
                "metadata_extraction": {
                    "file_properties": True,
                    "sheet_structure": True,
                    "cell_data": True,
                    "formulas": True,
                    "formatting": OPENPYXL_AVAILABLE,
                    "charts_detection": True,
                    "images_detection": True,
                    "named_ranges": True,
                    "merged_cells": True
                },
                "data_extraction": {
                    "max_recommended_rows": 1000,
                    "sample_data_default": 100,
                    "supports_formatting": True,
                    "data_types_supported": ["string", "number", "boolean", "formula", "date"]
                },
                "com_integration": {
                    "xlwings_available": XLWINGS_AVAILABLE,
                    "image_capture_ready": XLWINGS_AVAILABLE,
                    "advanced_formatting": XLWINGS_AVAILABLE
                },
                "requirements": {
                    "openpyxl": "Required for basic Excel operations",
                    "xlwings": "Optional for COM automation and image capture"
                },
                "limitations": [
                    ".xls files require additional setup for full support",
                    "Image capture requires xlwings and Windows Excel",
                    "Large files (>50MB) may have slower processing"
                ]
            }
            
            return capabilities
            
        except Exception as e:
            logger.exception(f"Error getting Excel capabilities: {str(e)}")
            return {"error": str(e)}


def _create_workbook_summary(metadata: Dict[str, Any]) -> WorkbookSummary:
    """
    Create a simplified workbook summary from full metadata.
    
    Args:
        metadata: Full metadata dictionary
        
    Returns:
        WorkbookSummary object
    """
    file_meta = metadata.get("fileMetadata", {})
    
    sheets_summary = []
    for sheet_data in metadata.get("sheets", []):
        used_range = sheet_data.get("usedRange", {})
        content_summary = sheet_data.get("contentSummary", {})
        
        sheet_summary = SheetContentSummary(
            sheet_name=sheet_data.get("sheetName", ""),
            sheet_index=sheet_data.get("sheetIndex", 0),
            used_range=used_range.get("address", ""),
            total_rows=used_range.get("totalRows", 0),
            total_columns=used_range.get("totalColumns", 0),
            cell_count=content_summary.get("totalCells", 0),
            formula_count=content_summary.get("formulaCells", 0),
            has_charts=sheet_data.get("chartCount", 0) > 0,
            has_images=sheet_data.get("imageCount", 0) > 0,
            merged_cells_count=len(sheet_data.get("mergedCells", []))
        )
        sheets_summary.append(sheet_summary)
    
    return WorkbookSummary(
        filename=file_meta.get("fileName", ""),
        total_sheets=metadata.get("totalSheets", 0),
        file_size=file_meta.get("fileSize", 0),
        created=file_meta.get("createdTime"),
        modified=file_meta.get("modifiedTime"),
        creator=file_meta.get("creator"),
        sheets=sheets_summary
    )
