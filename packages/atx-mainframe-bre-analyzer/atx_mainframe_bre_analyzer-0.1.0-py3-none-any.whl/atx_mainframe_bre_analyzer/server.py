#!/usr/bin/env python3
"""
MCP BRE Navigator Server
Provides structured navigation of Business Rules Engine (BRE) hierarchy
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio

# MCP imports
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import Tool, TextContent
    import mcp.types as types
    import mcp.server.stdio
except ImportError as e:
    print(f"MCP import error: {e}", file=sys.stderr)
    print("Please install mcp: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Initialize the MCP server
server = Server("bre-navigator")

class BRENavigator:
    """Business Rules Engine Navigator"""
    
    def __init__(self):
        self.app_level_bre = os.getenv("ATX_MF_APPLICATION_LEVEL_BRE")
        self.component_level_bre = os.getenv("ATX_MF_COMPONENT_LEVEL_BRE")
        
        if not self.app_level_bre or not self.component_level_bre:
            raise ValueError("BRE environment variables not set")
    
    def get_business_functions(self) -> List[Dict[str, Any]]:
        """Get all business functions from Application Level BRE"""
        functions = []
        
        if not Path(self.app_level_bre).exists():
            return functions
            
        for item in Path(self.app_level_bre).iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                function_info = {
                    "name": item.name,
                    "path": str(item),
                    "has_main_spec": (item / f"{item.name}.json").exists(),
                    "entry_points": self._get_entry_points(item)
                }
                functions.append(function_info)
        
        return sorted(functions, key=lambda x: x["name"])
    
    def _get_entry_points(self, function_dir: Path) -> List[Dict[str, Any]]:
        """Get entry points for a business function"""
        entry_points = []
        
        for item in function_dir.iterdir():
            if item.is_dir() and item.name.startswith("entrypoint-"):
                program_name = item.name.replace("entrypoint-", "")
                entry_point_info = {
                    "name": program_name,
                    "directory": item.name,
                    "path": str(item),
                    "has_spec": (item / f"entrypoint-{program_name}.json").exists(),
                    "component_dependencies": self._get_component_dependencies(program_name)
                }
                entry_points.append(entry_point_info)
        
        return sorted(entry_points, key=lambda x: x["name"])
    
    def _get_component_dependencies(self, program_name: str) -> Dict[str, List[str]]:
        """Get component level dependencies for a program"""
        dependencies = {
            "cobol": [],
            "jcl": []
        }
        
        # Check COBOL components
        cbl_dir = Path(self.component_level_bre) / "cbl"
        if cbl_dir.exists():
            for cbl_file in cbl_dir.glob("*.json"):
                if program_name.upper() in cbl_file.stem.upper():
                    dependencies["cobol"].append(cbl_file.name)
        
        # Check JCL components  
        jcl_dir = Path(self.component_level_bre) / "jcl"
        if jcl_dir.exists():
            for jcl_file in jcl_dir.glob("*.json"):
                if program_name.upper() in jcl_file.stem.upper():
                    dependencies["jcl"].append(jcl_file.name)
        
        return dependencies
    
    def get_all_component_files(self) -> Dict[str, List[str]]:
        """Get all component level files"""
        components = {
            "cobol": [],
            "jcl": []
        }
        
        # Get COBOL files
        cbl_dir = Path(self.component_level_bre) / "cbl"
        if cbl_dir.exists():
            components["cobol"] = sorted([f.name for f in cbl_dir.glob("*.json")])
        
        # Get JCL files
        jcl_dir = Path(self.component_level_bre) / "jcl"  
        if jcl_dir.exists():
            components["jcl"] = sorted([f.name for f in jcl_dir.glob("*.json")])
        
        return components
    
    def search_components_by_pattern(self, pattern: str) -> Dict[str, List[str]]:
        """Search component files by pattern"""
        results = {
            "cobol": [],
            "jcl": []
        }
        
        pattern_upper = pattern.upper()
        
        # Search COBOL files
        cbl_dir = Path(self.component_level_bre) / "cbl"
        if cbl_dir.exists():
            for cbl_file in cbl_dir.glob("*.json"):
                if pattern_upper in cbl_file.stem.upper():
                    results["cobol"].append(cbl_file.name)
        
        # Search JCL files
        jcl_dir = Path(self.component_level_bre) / "jcl"
        if jcl_dir.exists():
            for jcl_file in jcl_dir.glob("*.json"):
                if pattern_upper in jcl_file.stem.upper():
                    results["jcl"].append(jcl_file.name)
        
        return results

# Initialize navigator
navigator = BRENavigator()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available BRE navigation tools"""
    return [
        Tool(
            name="list_business_functions",
            description="List all business functions from Application Level BRE with their entry points and component dependencies",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_business_function_details",
            description="Get detailed information about a specific business function including all entry points and their component dependencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the business function (e.g., 'AccountManagement', 'BillingandPayment')"
                    }
                },
                "required": ["function_name"]
            }
        ),
        Tool(
            name="list_all_components",
            description="List all component level files (COBOL and JCL) available in the BRE",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="search_components",
            description="Search for component files by pattern/program name",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern or program name (e.g., 'COACTUPC', 'CBTRN')"
                    }
                },
                "required": ["pattern"]
            }
        ),
        Tool(
            name="get_bre_overview",
            description="Get complete BRE hierarchy overview with statistics",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Handle tool calls"""
    
    if name == "list_business_functions":
        functions = navigator.get_business_functions()
        
        result = {
            "business_functions": functions,
            "total_functions": len(functions),
            "summary": {
                "functions_with_specs": len([f for f in functions if f["has_main_spec"]]),
                "total_entry_points": sum(len(f["entry_points"]) for f in functions),
                "functions_with_entry_points": len([f for f in functions if f["entry_points"]])
            }
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "get_business_function_details":
        function_name = arguments.get("function_name")
        if not function_name:
            return [types.TextContent(type="text", text="Error: function_name is required")]
        
        functions = navigator.get_business_functions()
        function_details = next((f for f in functions if f["name"] == function_name), None)
        
        if not function_details:
            available = [f["name"] for f in functions]
            return [types.TextContent(
                type="text", 
                text=f"Error: Business function '{function_name}' not found. Available: {available}"
            )]
        
        return [types.TextContent(
            type="text",
            text=json.dumps(function_details, indent=2)
        )]
    
    elif name == "list_all_components":
        components = navigator.get_all_component_files()
        
        result = {
            "components": components,
            "summary": {
                "total_cobol_files": len(components["cobol"]),
                "total_jcl_files": len(components["jcl"]),
                "total_components": len(components["cobol"]) + len(components["jcl"])
            }
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "search_components":
        pattern = arguments.get("pattern")
        if not pattern:
            return [types.TextContent(type="text", text="Error: pattern is required")]
        
        results = navigator.search_components_by_pattern(pattern)
        
        result = {
            "search_pattern": pattern,
            "results": results,
            "summary": {
                "cobol_matches": len(results["cobol"]),
                "jcl_matches": len(results["jcl"]),
                "total_matches": len(results["cobol"]) + len(results["jcl"])
            }
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "get_bre_overview":
        functions = navigator.get_business_functions()
        components = navigator.get_all_component_files()
        
        overview = {
            "bre_directories": {
                "application_level": navigator.app_level_bre,
                "component_level": navigator.component_level_bre
            },
            "business_functions": {
                "total": len(functions),
                "with_specifications": len([f for f in functions if f["has_main_spec"]]),
                "with_entry_points": len([f for f in functions if f["entry_points"]]),
                "total_entry_points": sum(len(f["entry_points"]) for f in functions)
            },
            "component_files": {
                "cobol": len(components["cobol"]),
                "jcl": len(components["jcl"]),
                "total": len(components["cobol"]) + len(components["jcl"])
            },
            "function_list": [f["name"] for f in functions]
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(overview, indent=2)
        )]
    
    else:
        return [types.TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="bre-navigator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())