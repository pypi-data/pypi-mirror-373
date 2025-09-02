# AWS Transform for mainframe (ATX) - Mainframe BRE Analyzer

[![PyPI version](https://img.shields.io/pypi/v/atx-mainframe-bre-analyzer.svg)](https://pypi.org/project/atx-mainframe-bre-analyzer/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/atx-mainframe-bre-analyzer.svg?label=PyPI%20downloads)](https://pypi.org/project/atx-mainframe-bre-analyzer/)
[![Python versions](https://img.shields.io/pypi/pyversions/atx-mainframe-bre-analyzer.svg)](https://pypi.org/project/atx-mainframe-bre-analyzer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive tool for analyzing ATX Business Rules Extraction (BRE) output as part of **[AWS Transform for mainframe (ATX)](https://aws.amazon.com/transform/mainframe/)** initiatives. Can be used as both an MCP server and a Python library.

## Overview

This tool extends the **[AWS Transform for mainframe (ATX)](https://aws.amazon.com/transform/mainframe/) analysis workflow** by providing advanced Business Rules Extraction analysis capabilities for mainframe applications. It works with the BRE output produced by the ATX analysis step to enable deeper insights into business logic and modernization planning.

### ATX Integration Workflow

```
ATX Analysis → BRE Output + Application/Component Analysis → ATX Mainframe BRE Analyzer → Business Rules Analysis
```

1. **ATX Analysis**: Analyzes your mainframe codebase and produces BRE output
2. **ATX Mainframe BRE Analyzer**: Uses the BRE analysis results for business rules exploration
3. **Business Rules Analysis**: Provides tools for business function mapping, component discovery, and modernization planning

## Features

- **Business Function Analysis**: Navigate business functions and their entry points
- **Component Mapping**: Map business functions to COBOL and JCL components  
- **Search and Discovery**: Find components by pattern or program name
- **BRE Overview**: Get comprehensive statistics about your business rules
- **Modernization Planning**: Support microservices architecture planning
- **Dual Usage**: Works as both MCP server and Python library

## Prerequisites

- **ATX Analysis**: Must be completed first to generate the BRE output
- **BRE Directories**: Application Level and Component Level BRE analysis results
- **Same Codebase**: Use the identical codebase that was analyzed by ATX

## Installation

### For MCP Server Usage
No installation needed! The MCP configuration with `uvx` will automatically download and run the package.

### For Python Library Usage
```bash
pip install atx-mainframe-bre-analyzer
```

## Quick Start

### Configuration

Set these environment variables to point to your ATX BRE analysis outputs:

```bash
export ATX_MF_APPLICATION_LEVEL_BRE="/path/to/application/level/bre"
export ATX_MF_COMPONENT_LEVEL_BRE="/path/to/component/level/bre"
```

### As MCP Server

```json
{
  "mcpServers": {
    "atx-mainframe-bre-analyzer": {
      "command": "uvx",
      "args": ["atx-mainframe-bre-analyzer"],
      "env": {
        "ATX_MF_APPLICATION_LEVEL_BRE": "/path/to/application/level/bre",
        "ATX_MF_COMPONENT_LEVEL_BRE": "/path/to/component/level/bre"
      }
    }
  }
}
```

### As Python Library

```python
from atx_mainframe_bre_analyzer.server import BRENavigator
import os

# Set environment variables
os.environ['ATX_MF_APPLICATION_LEVEL_BRE'] = "/path/to/application/level/bre"
os.environ['ATX_MF_COMPONENT_LEVEL_BRE'] = "/path/to/component/level/bre"

# Initialize and analyze
navigator = BRENavigator()
functions = navigator.get_business_functions()
components = navigator.get_all_component_files()
```

## Available Tools

### Business Function Analysis
- `list_business_functions` - List all business functions with entry points
- `get_business_function_details` - Get detailed information about a specific business function

### Component Discovery  
- `list_all_components` - List all COBOL and JCL component files
- `search_components` - Search for component files by pattern or program name

### System Analysis
- `get_bre_overview` - Get complete BRE hierarchy overview with statistics

## Usage Examples

### Basic Analysis

```python
# Get all business functions
functions = navigator.get_business_functions()
print(f"Found {len(functions)} business functions")

# Get component overview
components = navigator.get_all_component_files()
print(f"COBOL: {len(components['cobol'])}, JCL: {len(components['jcl'])}")

# Search for specific components
results = navigator.search_components_by_pattern("COACT")
print(f"Found {len(results['cobol'])} COBOL matches")
```

### Business Function Discovery

```python
# Get details for a specific business function
for func in functions:
    if "Account" in func["name"]:
        print(f"Function: {func['name']}")
        print(f"Entry Points: {len(func['entry_points'])}")
        for ep in func['entry_points']:
            print(f"  - {ep['name']}: {ep['component_dependencies']}")
```

## ATX BRE Output Format

The BRE analysis is produced by the ATX analysis step and follows this structure:

**Application Level BRE:**
```
ApplicationLevelAnalysis/
├── BusinessFunction1/
│   ├── BusinessFunction1.json
│   ├── entrypoint-PROGRAM1/
│   └── entrypoint-PROGRAM2/
└── BusinessFunction2/
    └── ...
```

**Component Level BRE:**
```
ComponentLevelAnalysis/
├── cbl/
│   ├── PROGRAM1.json
│   └── PROGRAM2.json
└── jcl/
    ├── JOB1.json
    └── JOB2.json
```

**Note**: These directories are automatically generated by ATX analysis - you don't need to create them manually.

## AWS Transform Integration

This tool is designed to work seamlessly with [AWS Transform for mainframe (ATX)](https://aws.amazon.com/transform/mainframe/) workflows:

1. **Run ATX Analysis** on your mainframe codebase
2. **Use the BRE output** directories generated by ATX
3. **Launch this tool** (as MCP server or library) for business rules analysis
4. **Plan modernization** using business function insights
5. **Map to microservices** based on business logic boundaries

## License

MIT License - see LICENSE file for details.