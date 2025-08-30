"""
Excel-specific extractor using the shared Office SDK.

Provides comprehensive Excel workbook analysis including:
- Worksheet data extraction
- Chart and pivot table analysis
- Formula parsing and cell formatting
- Data validation rules
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

from volute_office import BaseOfficeExtractor, DocumentProperties, AnalysisResult
from volute_office.models import CellInfo, RangeInfo, ChartInfo, TableInfo

logger = logging.getLogger(__name__)

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    logger.warning("openpyxl not available - some features may be limited")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not available - data analysis features limited")


class ExcelExtractor(BaseOfficeExtractor):
    """Excel-specific document extractor using COM automation."""
    
    @property
    def app_name(self) -> str:
        return 'Excel.Application'
    
    @property
    def supported_extensions(self) -> List[str]:
        return ['.xlsx', '.xlsm', '.xlsb', '.xls', '.xlt', '.xltx', '.xltm', '.csv']
    
    def _open_document_impl(self, file_path: str, read_only: bool) -> Any:
        """Open Excel workbook using COM."""
        return self.app.Workbooks.Open(file_path, ReadOnly=read_only)
    
    def _close_document_impl(self) -> None:
        """Close Excel workbook."""
        if self.document:
            self.document.Close(False)  # Don't save changes
    
    def _extract_document_properties_impl(self) -> DocumentProperties:
        """Extract Excel workbook properties."""
        props = self.document.BuiltinDocumentProperties
        
        return DocumentProperties(
            title=self._get_property_safe(props, "Title"),
            author=self._get_property_safe(props, "Author"),
            subject=self._get_property_safe(props, "Subject"),
            keywords=self._get_property_safe(props, "Keywords"),
            comments=self._get_property_safe(props, "Comments"),
            category=self._get_property_safe(props, "Category"),
            company=self._get_property_safe(props, "Company"),
            manager=self._get_property_safe(props, "Manager"),
            created=self._get_date_property_safe(props, "Creation Date"),
            modified=self._get_date_property_safe(props, "Last Save Time"),
            last_author=self._get_property_safe(props, "Last Author"),
            revision_number=self._get_property_safe(props, "Revision Number"),
            application_name=self._get_property_safe(props, "Application Name"),
            security=self._get_property_safe(props, "Security")
        )
    
    def _extract_metadata_impl(self, **kwargs) -> Dict[str, Any]:
        """Extract comprehensive Excel workbook metadata."""
        include_data = kwargs.get('include_data', True)
        include_charts = kwargs.get('include_charts', True)
        include_pivot_tables = kwargs.get('include_pivot_tables', True)
        max_rows = kwargs.get('max_rows', 1000)
        max_cols = kwargs.get('max_cols', 100)
        
        metadata = {
            "workbook_info": self._extract_workbook_info(),
            "worksheets": [],
            "document_properties": self._extract_document_properties_impl().dict()
        }
        
        # Process each worksheet
        for worksheet in self.document.Worksheets:
            worksheet_data = self._extract_worksheet_metadata(
                worksheet, 
                include_data=include_data,
                include_charts=include_charts,
                include_pivot_tables=include_pivot_tables,
                max_rows=max_rows,
                max_cols=max_cols
            )
            metadata["worksheets"].append(worksheet_data)
        
        # Add workbook-level analysis
        metadata["analysis"] = self._analyze_workbook()
        
        return metadata
    
    def _extract_workbook_info(self) -> Dict[str, Any]:
        """Extract basic workbook information."""
        return {
            "name": self.document.Name,
            "full_name": self.document.FullName if hasattr(self.document, 'FullName') else None,
            "worksheet_count": self.document.Worksheets.Count,
            "has_vba": self.document.HasVBProject if hasattr(self.document, 'HasVBProject') else False,
            "calculation_mode": self._get_calculation_mode(),
            "protection": {
                "structure_protected": self.document.ProtectStructure if hasattr(self.document, 'ProtectStructure') else False,
                "windows_protected": self.document.ProtectWindows if hasattr(self.document, 'ProtectWindows') else False
            }
        }
    
    def _extract_worksheet_metadata(self, worksheet, include_data: bool = True,
                                  include_charts: bool = True, include_pivot_tables: bool = True,
                                  max_rows: int = 1000, max_cols: int = 100) -> Dict[str, Any]:
        """Extract metadata from a single worksheet."""
        
        worksheet_info = {
            "name": worksheet.Name,
            "index": worksheet.Index,
            "visible": worksheet.Visible != 0,  # xlSheetVisible = 0
            "protection": {
                "protected": worksheet.ProtectContents if hasattr(worksheet, 'ProtectContents') else False
            }
        }
        
        # Get used range information
        used_range = worksheet.UsedRange
        if used_range:
            worksheet_info["used_range"] = {
                "address": used_range.Address,
                "row_count": used_range.Rows.Count,
                "column_count": used_range.Columns.Count,
                "first_row": used_range.Row,
                "first_column": used_range.Column,
                "last_row": used_range.Row + used_range.Rows.Count - 1,
                "last_column": used_range.Column + used_range.Columns.Count - 1
            }
            
            # Extract data if requested
            if include_data:
                worksheet_info["data"] = self._extract_range_data(
                    used_range, max_rows, max_cols
                )
        else:
            worksheet_info["used_range"] = None
            worksheet_info["data"] = None
        
        # Extract charts
        if include_charts:
            worksheet_info["charts"] = self._extract_charts(worksheet)
        
        # Extract pivot tables
        if include_pivot_tables:
            worksheet_info["pivot_tables"] = self._extract_pivot_tables(worksheet)
        
        # Extract named ranges in this worksheet
        worksheet_info["named_ranges"] = self._extract_worksheet_names(worksheet)
        
        return worksheet_info
    
    def _extract_range_data(self, range_obj, max_rows: int, max_cols: int) -> Dict[str, Any]:
        """Extract data from an Excel range."""
        try:
            # Limit the range if it's too large
            actual_rows = min(range_obj.Rows.Count, max_rows)
            actual_cols = min(range_obj.Columns.Count, max_cols)
            
            # Get the limited range
            if actual_rows < range_obj.Rows.Count or actual_cols < range_obj.Columns.Count:
                limited_range = range_obj.Resize(actual_rows, actual_cols)
            else:
                limited_range = range_obj
            
            # Extract values
            values = limited_range.Value
            
            # Convert to list format
            if values is None:
                data = []
            elif isinstance(values, (list, tuple)):
                if isinstance(values[0], (list, tuple)):
                    # 2D array
                    data = [list(row) if row else [] for row in values]
                else:
                    # 1D array (single row)
                    data = [list(values)]
            else:
                # Single cell
                data = [[values]]
            
            # Extract formatting information for first few cells
            sample_formatting = self._extract_sample_formatting(limited_range, min(5, actual_rows))
            
            return {
                "values": data,
                "row_count": actual_rows,
                "column_count": actual_cols,
                "truncated": (actual_rows < range_obj.Rows.Count or actual_cols < range_obj.Columns.Count),
                "sample_formatting": sample_formatting
            }
            
        except Exception as e:
            logger.exception(f"Error extracting range data: {str(e)}")
            return {"error": str(e)}
    
    def _extract_sample_formatting(self, range_obj, sample_rows: int) -> List[Dict[str, Any]]:
        """Extract formatting information from sample cells."""
        formatting = []
        
        try:
            for row in range(1, min(sample_rows + 1, range_obj.Rows.Count + 1)):
                for col in range(1, min(6, range_obj.Columns.Count + 1)):  # Sample first 5 columns
                    cell = range_obj.Cells(row, col)
                    cell_format = {
                        "address": cell.Address,
                        "number_format": cell.NumberFormat if hasattr(cell, 'NumberFormat') else None,
                        "font": {
                            "name": cell.Font.Name if hasattr(cell, 'Font') else None,
                            "size": cell.Font.Size if hasattr(cell, 'Font') else None,
                            "bold": cell.Font.Bold if hasattr(cell, 'Font') else None,
                            "italic": cell.Font.Italic if hasattr(cell, 'Font') else None,
                        },
                        "fill_color": self._get_color_safe(cell.Interior) if hasattr(cell, 'Interior') else None,
                        "has_formula": str(cell.Formula).startswith('=') if hasattr(cell, 'Formula') and cell.Formula else False
                    }
                    formatting.append(cell_format)
        except Exception as e:
            logger.debug(f"Error extracting cell formatting: {str(e)}")
        
        return formatting
    
    def _extract_charts(self, worksheet) -> List[Dict[str, Any]]:
        """Extract chart information from worksheet."""
        charts = []
        
        try:
            for chart_obj in worksheet.ChartObjects:
                chart = chart_obj.Chart
                chart_info = {
                    "name": chart_obj.Name,
                    "chart_type": self._get_chart_type_name(chart.ChartType) if hasattr(chart, 'ChartType') else 'Unknown',
                    "title": chart.ChartTitle.Text if hasattr(chart, 'ChartTitle') and chart.HasTitle else None,
                    "position": {
                        "left": chart_obj.Left,
                        "top": chart_obj.Top, 
                        "width": chart_obj.Width,
                        "height": chart_obj.Height
                    },
                    "series_count": chart.SeriesCollection().Count if hasattr(chart, 'SeriesCollection') else 0,
                    "has_legend": chart.HasLegend if hasattr(chart, 'HasLegend') else False
                }
                charts.append(chart_info)
        except Exception as e:
            logger.debug(f"Error extracting charts: {str(e)}")
        
        return charts
    
    def _extract_pivot_tables(self, worksheet) -> List[Dict[str, Any]]:
        """Extract pivot table information."""
        pivot_tables = []
        
        try:
            for pivot_table in worksheet.PivotTables:
                pivot_info = {
                    "name": pivot_table.Name,
                    "table_range": pivot_table.TableRange2.Address if hasattr(pivot_table, 'TableRange2') else None,
                    "source_data": str(pivot_table.SourceData) if hasattr(pivot_table, 'SourceData') else None,
                    "fields": {
                        "row_fields": [field.Name for field in pivot_table.RowFields] if hasattr(pivot_table, 'RowFields') else [],
                        "column_fields": [field.Name for field in pivot_table.ColumnFields] if hasattr(pivot_table, 'ColumnFields') else [],
                        "data_fields": [field.Name for field in pivot_table.DataFields] if hasattr(pivot_table, 'DataFields') else []
                    }
                }
                pivot_tables.append(pivot_info)
        except Exception as e:
            logger.debug(f"Error extracting pivot tables: {str(e)}")
        
        return pivot_tables
    
    def _extract_worksheet_names(self, worksheet) -> List[Dict[str, Any]]:
        """Extract named ranges that refer to this worksheet."""
        names = []
        
        try:
            for name in self.document.Names:
                if worksheet.Name in str(name.RefersTo):
                    names.append({
                        "name": name.Name,
                        "refers_to": str(name.RefersTo),
                        "visible": name.Visible if hasattr(name, 'Visible') else True
                    })
        except Exception as e:
            logger.debug(f"Error extracting named ranges: {str(e)}")
        
        return names
    
    def _analyze_workbook(self) -> Dict[str, Any]:
        """Perform high-level analysis of the workbook."""
        analysis = {
            "total_worksheets": self.document.Worksheets.Count,
            "visible_worksheets": 0,
            "total_cells_with_data": 0,
            "total_formulas": 0,
            "total_charts": 0,
            "total_pivot_tables": 0,
            "has_external_connections": False,
            "complexity_score": 0
        }
        
        try:
            for worksheet in self.document.Worksheets:
                if worksheet.Visible != 0:  # xlSheetHidden = -1, xlSheetVeryHidden = 2
                    analysis["visible_worksheets"] += 1
                
                # Count used cells
                used_range = worksheet.UsedRange
                if used_range:
                    analysis["total_cells_with_data"] += used_range.Cells.Count
                
                # Count charts
                analysis["total_charts"] += worksheet.ChartObjects.Count
                
                # Count pivot tables  
                analysis["total_pivot_tables"] += worksheet.PivotTables.Count
            
            # Calculate complexity score
            analysis["complexity_score"] = self._calculate_complexity_score(analysis)
            
        except Exception as e:
            logger.debug(f"Error in workbook analysis: {str(e)}")
        
        return analysis
    
    def _calculate_complexity_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate a complexity score for the workbook."""
        score = 0
        score += analysis["total_worksheets"] * 1
        score += analysis["total_charts"] * 3
        score += analysis["total_pivot_tables"] * 5
        score += min(analysis["total_cells_with_data"] // 1000, 10)  # Cap at 10 points
        return min(score, 100)  # Cap at 100
    
    def _get_property_safe(self, props, prop_name: str) -> Optional[str]:
        """Safely get a document property."""
        try:
            return str(props(prop_name).Value)
        except:
            return None
    
    def _get_date_property_safe(self, props, prop_name: str) -> Optional[datetime]:
        """Safely get a date document property."""
        try:
            value = props(prop_name).Value
            if isinstance(value, datetime):
                return value
            return None
        except:
            return None
    
    def _get_calculation_mode(self) -> str:
        """Get Excel calculation mode."""
        try:
            mode = self.app.Calculation
            modes = {
                -4105: "Automatic",  # xlCalculationAutomatic
                -4135: "Manual",     # xlCalculationManual
                2: "Semiautomatic"   # xlCalculationSemiautomatic
            }
            return modes.get(mode, "Unknown")
        except:
            return "Unknown"
    
    def _get_chart_type_name(self, chart_type: int) -> str:
        """Convert chart type number to name."""
        chart_types = {
            51: "Column Clustered",
            52: "Column Stacked", 
            53: "Column Stacked 100%",
            4: "Line",
            5: "Pie",
            -4120: "Bar Clustered",
            69: "Scatter",
            15: "Area"
        }
        return chart_types.get(chart_type, f"Type {chart_type}")
    
    def _get_color_safe(self, interior_obj) -> Optional[str]:
        """Safely get color from interior object."""
        try:
            color_index = interior_obj.ColorIndex
            if color_index == -4142:  # xlColorIndexNone
                return None
            return f"ColorIndex_{color_index}"
        except:
            return None
