#!/usr/bin/env python3
"""
Simple Excel Parser for Natural Commands

This is a clean, purpose-built parser specifically designed for the natural command syntax
that AI agents generate. It bypasses the complex legacy markdown parser entirely.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union, Tuple

logger = logging.getLogger(__name__)

def parse_and_execute_natural_commands(excel_path: str, commands_data: Dict[str, Dict]) -> List[Dict[str, Any]]:
    """
    Parse natural commands data and execute them directly on Excel.
    
    This bypasses the complex markdown conversion and uses a direct approach.
    
    Args:
        excel_path: Path to Excel file
        commands_data: Dictionary with sheet names as keys and cell operations as values
        
    Returns:
        List of updated cell information
    """
    logger.info(f"Parsing and executing natural commands on {excel_path}")
    
    try:
        from writer.excel_writer import ExcelWriter
        
        # Initialize Excel writer
        writer = ExcelWriter()
        
        # Convert natural commands to Excel writer format
        excel_data = {}
        
        for sheet_name, cells in commands_data.items():
            logger.info(f"Processing sheet '{sheet_name}' with {len(cells)} cells")
            excel_data[sheet_name] = []
            
            for cell_ref, cell_data in cells.items():
                logger.debug(f"Processing cell {cell_ref}: {cell_data}")
                
                # Create cell entry for Excel writer
                cell_entry = {"cell": cell_ref}
                
                if isinstance(cell_data, dict):
                    # Complex cell with formula and formatting
                    formula = cell_data.get('formula')
                    
                    # Add formula/value if present
                    if formula and formula != '[no_change]':
                        cell_entry["formula"] = formula
                    
                    # Add formatting properties
                    if cell_data.get('b'):  # bold
                        cell_entry["bold"] = True
                    if cell_data.get('it'):  # italic
                        cell_entry["italic"] = True
                    if cell_data.get('u'):  # underline
                        cell_entry["underline"] = True
                    
                    # Background color
                    if cell_data.get('fill'):
                        cell_entry["fill_color"] = cell_data['fill']
                    
                    # Font color
                    if cell_data.get('font'):
                        cell_entry["font_color"] = cell_data['font']
                    
                    # Alignment
                    if cell_data.get('ha'):
                        cell_entry["alignment"] = cell_data['ha']
                    
                    # Font size
                    if cell_data.get('sz'):
                        cell_entry["font_size"] = int(cell_data['sz'])
                        
                else:
                    # Simple cell with just a value
                    cell_entry["formula"] = str(cell_data)
                
                logger.debug(f"Excel writer entry for {cell_ref}: {cell_entry}")
                excel_data[sheet_name].append(cell_entry)
        
        logger.info(f"Converted data for Excel writer: {excel_data}")
        
        # Execute the Excel operations
        logger.info("Executing Excel write operation...")
        success, updated_cells = writer.write_to_existing(
            data=excel_data,
            output_filepath=excel_path,
            create_pending=False,
            save=True
        )
        
        if success:
            logger.info(f"Excel write operation successful. Updated cells: {updated_cells}")
            return updated_cells or []
        else:
            logger.error("Excel write operation failed")
            return []
            
    except Exception as e:
        logger.error(f"Error in parse_and_execute_natural_commands: {str(e)}", exc_info=True)
        raise

def execute_row_column_operations(excel_path: str, operations: List[Dict]) -> Dict[str, Any]:
    """Execute row/column operations directly."""
    if not operations:
        return {"success": True, "operations_count": 0}
    
    logger.info(f"Executing {len(operations)} row/column operations")
    
    try:
        import xlwings as xw
        
        # Open workbook
        wb = xw.Book(excel_path)
        results = []
        
        for op in operations:
            try:
                sheet_name = op['sheet']
                ws = wb.sheets[sheet_name]
                
                if op['operation'] == 'insert_row':
                    ws.api.Rows(op['row_number']).Insert()
                    results.append(f"Inserted row {op['row_number']}")
                
                elif op['operation'] == 'delete_row':
                    ws.api.Rows(op['row_number']).Delete()
                    results.append(f"Deleted row {op['row_number']}")
                
                elif op['operation'] == 'hide_row':
                    ws.api.Rows(op['row_number']).Hidden = True
                    results.append(f"Hid row {op['row_number']}")
                
                elif op['operation'] == 'resize_column':
                    ws.api.Columns(op['column']).ColumnWidth = op['width']
                    results.append(f"Set column {op['column']} width to {op['width']}")
                
                elif op['operation'] == 'insert_column':
                    ws.api.Columns(op['column']).Insert()
                    results.append(f"Inserted column {op['column']}")
                
                elif op['operation'] == 'delete_column':
                    ws.api.Columns(op['column']).Delete()
                    results.append(f"Deleted column {op['column']}")
                
                elif op['operation'] == 'hide_column':
                    ws.api.Columns(op['column']).Hidden = True
                    results.append(f"Hid column {op['column']}")
                    
            except Exception as e:
                logger.error(f"Error in operation {op}: {e}")
                results.append(f"Error in {op['operation']}: {str(e)}")
        
        # Save and close
        wb.save()
        wb.close()
        
        return {
            "success": True,
            "operations_count": len(operations),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Row/column operations failed: {e}", exc_info=True)
        return {"error": f"Row/column operations failed: {str(e)}"}

def execute_sheet_operations(excel_path: str, operations: List[Dict]) -> Dict[str, Any]:
    """Execute sheet operations directly."""
    if not operations:
        return {"success": True, "operations_count": 0}
    
    logger.info(f"Executing {len(operations)} sheet operations")
    
    try:
        import xlwings as xw
        
        # Open workbook
        wb = xw.Book(excel_path)
        results = []
        
        for op in operations:
            try:
                if op['operation'] == 'add_sheet':
                    wb.sheets.add(name=op['name'])
                    results.append(f"Added sheet '{op['name']}'")
                
                elif op['operation'] == 'delete_sheet':
                    if op['name'] in [sheet.name for sheet in wb.sheets]:
                        wb.sheets[op['name']].delete()
                        results.append(f"Deleted sheet '{op['name']}'")
                    else:
                        results.append(f"Sheet '{op['name']}' not found")
                
                elif op['operation'] == 'rename_sheet':
                    if op['old_name'] in [sheet.name for sheet in wb.sheets]:
                        wb.sheets[op['old_name']].name = op['new_name']
                        results.append(f"Renamed sheet '{op['old_name']}' to '{op['new_name']}'")
                    else:
                        results.append(f"Sheet '{op['old_name']}' not found")
                        
            except Exception as e:
                logger.error(f"Error in sheet operation {op}: {e}")
                results.append(f"Error in {op['operation']}: {str(e)}")
        
        # Save and close
        wb.save()
        wb.close()
        
        return {
            "success": True,
            "operations_count": len(operations),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Sheet operations failed: {e}", exc_info=True)
        return {"error": f"Sheet operations failed: {str(e)}"}
