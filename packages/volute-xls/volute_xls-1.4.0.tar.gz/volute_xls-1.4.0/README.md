# Volute-XLS: Excel Integration for AI Applications

[![PyPI version](https://badge.fury.io/py/volute-xls.svg)](https://badge.fury.io/py/volute-xls)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive **Model Context Protocol (MCP) server** that enables AI agents to interact with Microsoft Excel spreadsheets through advanced metadata extraction, content analysis, and multimodal sheet image capture.

## 🚀 Features

### 📊 **Excel Analysis & Metadata Extraction**
- **Comprehensive workbook analysis** - File properties, sheet structure, named ranges
- **Detailed sheet content analysis** - Cell data, formulas, data types, merged cells
- **Chart and image detection** - Identify visual elements in spreadsheets  
- **Sample data extraction** - Get representative cell data for content understanding
- **Cross-platform support** - Works on Windows, macOS, and Linux

### 🖼️ **Multimodal Sheet Image Capture** (Windows + xlwings)
- **Full sheet capture** - Export entire worksheets as PNG images
- **Range-specific capture** - Target specific cell ranges for focused analysis
- **Zoom control** - Adjust capture zoom levels (10% to 400%)
- **Base64 encoding** - Ready for multimodal LLM analysis
- **Thread-safe operations** - Reliable concurrent Excel automation

### 📝 **Advanced Excel Operations** (v1.2.0+)
- **Natural language commands** - `A1 = "Hello"`, `B1 bold`, `C1 fill #FF0000`
- **Formula execution** - Complex formulas with `=SUM()`, `=IF()`, `=AVERAGE()`, etc.
- **Comprehensive formatting** - Colors, fonts, sizes, borders, alignment
- **Sheet management** - Column/row operations, sheet creation/deletion
- **Multi-sheet support** - Work across multiple worksheets seamlessly
- **Data validation** - Real-time verification of operations

### 🔧 **Dual Architecture**
- **Local Server** - Full COM automation with xlwings for Windows Excel integration
- **Cloud Server** - Cross-platform openpyxl-based analysis without local requirements
- **FastMCP Integration** - Built on the Model Context Protocol standard
- **SDK Client Library** - Easy programmatic access to all tools

## 📦 Installation

### Basic Installation (Cross-platform)
```bash
pip install volute-xls
```

### Full Windows Installation (with image capture)
```bash
pip install volute-xls[windows]
# or for all features
pip install volute-xls[full]
```

### Development Installation
```bash
pip install volute-xls[dev]
```

## 🏃‍♂️ Quick Start

### 1. Start the Local Server
```bash
# HTTP server (default)
volute-xls-local

# STDIO for MCP clients  
volute-xls-local --transport stdio
```

### 2. Use with MCP Configuration
Add to your MCP client configuration:

**Option A: Using installed package command**
```json
{
  "volute-xls-local": {
    "command": "volute-xls-local",
    "args": ["--transport", "stdio"],
    "env": {},
    "working_directory": null
  }
}
```

**Option B: Using Python module (alternative)**
```json
{
  "volute-xls-local": {
    "command": "python",
    "args": [
      "-m",
      "volute_xls.server_local",
      "--transport",
      "stdio"
    ],
    "env": {},
    "working_directory": null
  }
}
```

### 3. Programmatic Usage
```python
from volute_xls import create_client

# Extract Excel metadata
async with create_client("local") as client:
    metadata = await client.extract_excel_metadata(
        "path/to/workbook.xlsx",
        include_sheet_content=True,
        include_sheet_data=True
    )
    print(f"Found {len(metadata['data']['sheets'])} sheets")

# Capture sheet images (Windows + xlwings)
async with create_client("local") as client:
    images = await client.capture_excel_sheets(
        "path/to/workbook.xlsx",
        sheet_names=["Sheet1", "Dashboard"],
        image_width=1200,
        image_height=800
    )
    # Images returned as base64-encoded PNG data
```

## 🛠️ Available Tools

### `extract_excel_metadata`
Extract comprehensive metadata from Excel workbooks including file properties, sheet structure, cell content summary, and named ranges.

**Parameters:**
- `excel_path` (str): Path to Excel file (.xlsx, .xlsm, .xls)
- `include_sheet_content` (bool): Include detailed sheet analysis
- `include_sheet_data` (bool): Include sample cell data  
- `output_format` (str): "json" or "summary"

### `analyze_excel_sheets`
Perform focused analysis of specific worksheets with detailed content extraction and optional sample data.

**Parameters:**
- `excel_path` (str): Path to Excel file
- `sheet_names` (list): Specific sheets to analyze (None for all)
- `include_data_sample` (bool): Include sample data
- `max_rows` (int): Maximum rows in sample
- `include_formatting` (bool): Include cell formatting

### `capture_excel_sheets` (Windows + xlwings)
Capture Excel worksheets as PNG images for multimodal analysis.

**Parameters:**
- `excel_path` (str): Path to Excel file
- `sheet_names` (list): Sheet names to capture
- `image_width` (int): Image width (200-4000px)
- `image_height` (int): Image height (200-4000px)
- `zoom_level` (float): Zoom percentage (10-400%)

### `capture_excel_ranges` (Windows + xlwings)
Capture specific cell ranges as images for detailed analysis.

**Parameters:**
- `excel_path` (str): Path to Excel file
- `sheet_ranges` (dict): {"SheetName": ["A1:C10", "E1:G5"]}
- `image_width` (int): Image width (100-2000px)
- `image_height` (int): Image height (100-2000px)

### `excel_edit` (v1.2.0+) 
Execute natural language Excel operations to modify spreadsheets.

**Parameters:**
- `excel_path` (str): Path to Excel file
- `commands` (str): Natural language commands like:
  - `A1 = "Hello World"` - Set cell values
  - `B1 bold` - Apply formatting
  - `C1 fill #FF0000` - Set colors
  - `D1 = =SUM(A1:C1)` - Insert formulas
  - `resize column A 15` - Adjust dimensions
  - `switch to Sheet2` - Navigate sheets

**Example Commands:**
```
A1 = "🏢 COMPANY DASHBOARD"
A1 bold
A1 fill #0000FF
A1 font #FFFFFF
B3 = =SUM(A1:A10)
resize column A 20
```

## 🌐 Architecture

### Local Server (`volute-xls-local`)
- **Full Excel Integration** - COM automation via xlwings
- **Image Capture** - Native Excel sheet-to-image export
- **Local File Access** - Direct file system operations
- **Thread Safety** - Concurrent Excel operations
- **Windows Optimized** - Best performance on Windows with Excel installed

### Cloud Server (`volute-xls-server`)
- **Cross-Platform** - Pure Python openpyxl-based analysis
- **No Excel Required** - Works without Microsoft Excel
- **Scalable** - Cloud deployment ready
- **Limited Features** - Metadata and analysis only (no image capture)

## 📋 Requirements

### Basic Requirements (All Platforms)
- Python 3.8+
- fastmcp >= 2.0.0
- openpyxl >= 3.0.0
- Pillow >= 9.0.0

### Windows Image Capture Requirements
- Microsoft Excel installed
- xlwings >= 0.30.0
- pywin32 >= 306

### Supported File Formats
- **.xlsx** - Excel 2007+ workbooks
- **.xlsm** - Excel macro-enabled workbooks  
- **.xls** - Legacy Excel workbooks (limited support)

## 🔧 Configuration

### Environment Variables
```bash
# Local server configuration
LOCAL_SERVER_NAME="Volute-XLS-Local"
LOCAL_SERVER_HOST="127.0.0.1"
LOCAL_SERVER_PORT="8002"

# Cloud server configuration  
CLOUD_SERVER_NAME="Volute-XLS-Cloud"
CLOUD_SERVER_HOST="0.0.0.0"
CLOUD_SERVER_PORT="8000"
```

### Server Options
```bash
# Start local server with custom settings
volute-xls-local --host 0.0.0.0 --port 8080

# Start cloud server
volute-xls-server --port 8000
```

## 🧪 Testing

```bash
# Install development dependencies
pip install volute-xls[dev]

# Run tests
pytest tests/

# Test with sample Excel file
python -c "
import asyncio
from volute_xls import create_client

async def test():
    async with create_client('local') as client:
        caps = await client.get_excel_capabilities()
        print('Excel capabilities:', caps)

asyncio.run(test())
"
```

## 🤝 Integration Examples

### Claude Desktop MCP Configuration
```json
{
  "mcpServers": {
    "volute-xls-local": {
      "command": "volute-xls-local",
      "args": ["--transport", "stdio"]
    }
  }
}
```

### Programmatic Analysis Pipeline
```python
import asyncio
from volute_xls import VoluteXLSLocalClient

async def analyze_workbook(file_path):
    async with VoluteXLSLocalClient() as client:
        # 1. Extract metadata
        metadata = await client.extract_excel_metadata(file_path)
        
        # 2. Analyze key sheets
        key_sheets = ["Summary", "Data", "Charts"]
        analysis = await client.analyze_excel_sheets(
            file_path, 
            sheet_names=key_sheets,
            include_data_sample=True
        )
        
        # 3. Capture images for multimodal analysis  
        if analysis.get('success'):
            images = await client.capture_excel_sheets(
                file_path,
                sheet_names=key_sheets
            )
            return {
                'metadata': metadata,
                'analysis': analysis, 
                'images': images
            }

# Usage
result = asyncio.run(analyze_workbook("financial_report.xlsx"))
```

## 📚 Documentation

- **API Reference** - [docs/api.md](docs/api.md)
- **Developer Guide** - [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **Examples** - [examples/](examples/)
- **Troubleshooting** - [docs/troubleshooting.md](docs/troubleshooting.md)

## 🛡️ Security & Privacy

- **Local Processing** - All Excel analysis happens locally
- **No Data Upload** - Files never leave your machine with local server
- **Thread Safety** - Concurrent operations are protected
- **Resource Management** - Automatic cleanup of temporary files and Excel instances

## 🗺️ Roadmap

- [ ] **Enhanced Chart Analysis** - Detailed chart metadata extraction
- [ ] **Pivot Table Support** - Analysis of pivot tables and data models
- [ ] **VBA Code Detection** - Identify and analyze VBA macros
- [ ] **Performance Optimization** - Faster processing of large workbooks
- [ ] **Additional Image Formats** - Support for JPEG, SVG export
- [ ] **Cloud Image Capture** - Server-side image generation without xlwings

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
git clone https://gitlab.com/coritan/volute-xls.git
cd volute-xls
pip install -e .[dev,full]
pre-commit install
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastMCP** - For the excellent Model Context Protocol framework
- **openpyxl** - For cross-platform Excel file processing  
- **xlwings** - For Windows Excel COM automation
- **Pillow** - For image processing capabilities
- **Model Context Protocol** - For the agent integration standard

---

**Created with ❤️ for the AI agent community**

For questions, issues, or feature requests, please visit our [GitLab repository](https://gitlab.com/coritan/volute-xls) or [open an issue](https://gitlab.com/coritan/volute-xls/-/issues).
