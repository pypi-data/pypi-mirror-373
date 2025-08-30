#!/usr/bin/env python3
"""
Excel Export Tools - Print layout and PDF export functionality.
"""

import os
import logging
import json
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

def excel_export_to_pdf(
    excel_path: str,
    output_path: str = None,
    print_settings: dict = None,
    sheets: list = None,
    overwrite: bool = False
) -> str:
    """
    Export Excel file to PDF with print layout settings.
    
    This function uses xlwings COM automation to:
    1. Configure print layout settings (margins, orientation, scaling, etc.)
    2. Export the configured workbook to PDF
    
    Args:
        excel_path: Path to the Excel file to export
        output_path: Path for the output PDF (default: same as Excel with .pdf)
        print_settings: Dictionary of print settings to apply:
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
        sheets: List of sheet names to include (default: all sheets)
        overwrite: Whether to overwrite existing PDF file
        
    Returns:
        JSON string with export results
    
    Example Print Settings:
        {
            "orientation": "landscape",
            "paper_size": "letter",
            "fit_to_pages": [1, 0],  # Fit to 1 page wide, auto height
            "margins": [0.5, 0.5, 0.5, 0.5],  # Inches
            "center_horizontal": True,
            "center_vertical": False,
            "print_gridlines": False,
            "print_titles": True,
            "header": {
                "left": "&[Date]",
                "center": "Monthly Report",
                "right": "Page &[Page] of &[Pages]"
            },
            "footer": {
                "left": "",
                "center": "&[File]",
                "right": ""
            }
        }
    """
    try:
        import xlwings as xw
        
        # Validate input file
        if not os.path.exists(excel_path):
            return json.dumps({
                "success": False,
                "error": f"Excel file not found: {excel_path}"
            })
        
        # Set default output path if not provided
        if not output_path:
            output_path = str(Path(excel_path).with_suffix('.pdf'))
            
        # Check if output file exists and handle overwrite
        if os.path.exists(output_path) and not overwrite:
            return json.dumps({
                "success": False,
                "error": f"PDF file already exists: {output_path}. Use overwrite=True to replace."
            })
            
        # Default print settings if none provided
        if not print_settings:
            print_settings = {
                "orientation": "portrait",
                "paper_size": "letter",
                "fit_to_pages": [1, 0],
                "margins": [0.75, 0.75, 0.75, 0.75],
                "center_horizontal": True,
                "center_vertical": False,
                "print_gridlines": False,
                "print_titles": True
            }
            
        # Open Excel with xlwings
        with xw.App(visible=False) as app:
            wb = app.books.open(excel_path)
            
            try:
                # Get sheets to process
                if not sheets:
                    sheets = [sheet.name for sheet in wb.sheets]
                    
                # Validate requested sheets exist
                for sheet_name in sheets:
                    if sheet_name not in [s.name for s in wb.sheets]:
                        return json.dumps({
                            "success": False,
                            "error": f"Sheet not found: {sheet_name}"
                        })
                
                # Configure each sheet
                for sheet_name in sheets:
                    ws = wb.sheets[sheet_name]
                    
                    # Get page setup object
                    page_setup = ws.page_setup
                    
                    # Set orientation
                    if print_settings.get("orientation"):
                        page_setup.orientation = (
                            xw.constants.PageOrientation.xlLandscape
                            if print_settings["orientation"].lower() == "landscape"
                            else xw.constants.PageOrientation.xlPortrait
                        )
                    
                    # Set paper size
                    if print_settings.get("paper_size"):
                        paper_sizes = {
                            "letter": xw.constants.PaperSize.xlPaperLetter,
                            "legal": xw.constants.PaperSize.xlPaperLegal,
                            "a4": xw.constants.PaperSize.xlPaperA4,
                            "a3": xw.constants.PaperSize.xlPaperA3
                        }
                        size_name = print_settings["paper_size"].lower()
                        if size_name in paper_sizes:
                            page_setup.paper_size = paper_sizes[size_name]
                    
                    # Set page fitting
                    if print_settings.get("fit_to_pages"):
                        fit_width, fit_height = print_settings["fit_to_pages"]
                        page_setup.fit_to_pages_wide = fit_width
                        page_setup.fit_to_pages_tall = fit_height
                    
                    # Set margins (in inches)
                    if print_settings.get("margins"):
                        left, right, top, bottom = print_settings["margins"]
                        page_setup.left_margin = left
                        page_setup.right_margin = right
                        page_setup.top_margin = top
                        page_setup.bottom_margin = bottom
                    
                    # Set centering
                    if print_settings.get("center_horizontal") is not None:
                        page_setup.center_horizontally = print_settings["center_horizontal"]
                    if print_settings.get("center_vertical") is not None:
                        page_setup.center_vertically = print_settings["center_vertical"]
                    
                    # Set gridlines
                    if print_settings.get("print_gridlines") is not None:
                        page_setup.print_gridlines = print_settings["print_gridlines"]
                    
                    # Set print titles
                    if print_settings.get("print_titles") is not None:
                        ws.print_titles = print_settings["print_titles"]
                    
                    # Set headers and footers
                    if print_settings.get("header"):
                        h = print_settings["header"]
                        ws.api.PageSetup.LeftHeader = h.get("left", "")
                        ws.api.PageSetup.CenterHeader = h.get("center", "")
                        ws.api.PageSetup.RightHeader = h.get("right", "")
                    
                    if print_settings.get("footer"):
                        f = print_settings["footer"]
                        ws.api.PageSetup.LeftFooter = f.get("left", "")
                        ws.api.PageSetup.CenterFooter = f.get("center", "")
                        ws.api.PageSetup.RightFooter = f.get("right", "")
                
                # Export to PDF
                try:
                    if len(sheets) == 1:
                        wb.sheets[sheets[0]].api.ExportAsFixedFormat(
                            0,  # PDF format
                            output_path
                        )
                    else:
                        wb.api.ExportAsFixedFormat(
                            0,  # PDF format
                            output_path,
                            IgnorePrintAreas=False
                        )
                        
                except Exception as e:
                    return json.dumps({
                        "success": False,
                        "error": f"Failed to export PDF: {str(e)}"
                    })
                
                return json.dumps({
                    "success": True,
                    "message": "Successfully exported to PDF",
                    "excel_file": excel_path,
                    "pdf_file": output_path,
                    "sheets_processed": sheets,
                    "print_settings": print_settings
                })
                
            finally:
                wb.close()
                
    except ImportError:
        return json.dumps({
            "success": False,
            "error": "xlwings library not available. Install with: pip install xlwings"
        })
    except Exception as e:
        logger.exception("Error in Excel PDF export")
        return json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        })
