import os
import json
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp.tools import Tool
from ..dependency_manager import get_dependency_manager


def read_component_source(component_name: str) -> str:
    """Read the source code content of a mainframe component.
    
    This tool reads the actual source code file for a given component name.
    The file path is resolved using the component's registered path and the 
    ATX_MF_CODE_BASE environment variable.
    
    Args:
        component_name: Name of the component to read
        
    Returns:
        The source code content of the component or error message
    """
    dm = get_dependency_manager()
    info = dm.get_component_info(component_name)
    
    if not info:
        return f"Component '{component_name}' not found"
    
    file_path = info.get('path', '')
    if not file_path:
        return f"No file path registered for component '{component_name}'"
    
    # Resolve absolute path
    code_base = os.getenv('ATX_MF_CODE_BASE', '')
    if not os.path.isabs(file_path) and code_base:
        absolute_path = os.path.join(code_base, file_path)
    else:
        absolute_path = file_path
    
    try:
        if not os.path.exists(absolute_path):
            return f"Source file not found: {absolute_path}"
        
        with open(absolute_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        return json.dumps({
            "component_name": component_name,
            "file_path": absolute_path,
            "file_size": len(content),
            "line_count": len(content.splitlines()),
            "content": content
        }, indent=2)
        
    except Exception as e:
        return f"Error reading source file '{absolute_path}': {str(e)}"


def get_component_source_info(component_name: str) -> str:
    """Get component information with explicit source code access details.
    
    This tool provides component information along with confirmation that 
    source files are accessible via the ATX_MF_CODE_BASE environment variable.
    It includes file existence checks and accessibility status.
    
    Args:
        component_name: Name of the component
        
    Returns:
        JSON string with component info and source access details
    """
    dm = get_dependency_manager()
    info = dm.get_component_info(component_name)
    
    if not info:
        return f"Component '{component_name}' not found"
    
    # Add component name to the info
    result = info.copy()
    result['name'] = component_name
    
    # Add source code accessibility information
    file_path = info.get('path', '')
    code_base = os.getenv('ATX_MF_CODE_BASE', '')
    
    if file_path:
        # Resolve absolute path
        if not os.path.isabs(file_path) and code_base:
            absolute_path = os.path.join(code_base, file_path)
        else:
            absolute_path = file_path
        
        result['absolute_path'] = absolute_path
        result['file_accessible'] = os.path.exists(absolute_path)
        result['code_base_configured'] = bool(code_base)
        
        if os.path.exists(absolute_path):
            try:
                stat_info = os.stat(absolute_path)
                result['file_size'] = stat_info.st_size
                result['last_modified'] = stat_info.st_mtime
            except Exception:
                pass
    else:
        result['absolute_path'] = None
        result['file_accessible'] = False
        result['code_base_configured'] = bool(code_base)
    
    result['source_access_note'] = "Source code can be accessed using read_component_source tool or by reading the file at absolute_path"
    
    return json.dumps(result, indent=2)


def list_component_directory(component_name: str) -> str:
    """List files in the directory containing a mainframe component.
    
    This tool lists all files in the same directory as the specified component,
    which can be useful for discovering related files, includes, or documentation.
    
    Args:
        component_name: Name of the component
        
    Returns:
        JSON string with directory listing or error message
    """
    dm = get_dependency_manager()
    info = dm.get_component_info(component_name)
    
    if not info:
        return f"Component '{component_name}' not found"
    
    file_path = info.get('path', '')
    if not file_path:
        return f"No file path registered for component '{component_name}'"
    
    # Resolve absolute path
    code_base = os.getenv('ATX_MF_CODE_BASE', '')
    if not os.path.isabs(file_path) and code_base:
        absolute_path = os.path.join(code_base, file_path)
    else:
        absolute_path = file_path
    
    directory = os.path.dirname(absolute_path)
    
    try:
        if not os.path.exists(directory):
            return f"Directory not found: {directory}"
        
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                try:
                    stat_info = os.stat(item_path)
                    files.append({
                        "name": item,
                        "path": item_path,
                        "size": stat_info.st_size,
                        "last_modified": stat_info.st_mtime
                    })
                except Exception:
                    files.append({
                        "name": item,
                        "path": item_path,
                        "size": None,
                        "last_modified": None
                    })
        
        return json.dumps({
            "component_name": component_name,
            "directory": directory,
            "files": sorted(files, key=lambda x: x['name']),
            "file_count": len(files)
        }, indent=2)
        
    except Exception as e:
        return f"Error listing directory '{directory}': {str(e)}"


def validate_source_access() -> str:
    """Validate that source code files are accessible for all components.
    
    This tool checks all registered components to verify that their source
    files can be accessed. It provides a summary of accessibility status
    and identifies any components with missing or inaccessible files.
    
    Returns:
        JSON string with validation results
    """
    dm = get_dependency_manager()
    stats = dm.get_statistics()
    
    code_base = os.getenv('ATX_MF_CODE_BASE', '')
    accessible_count = 0
    inaccessible_count = 0
    no_path_count = 0
    accessible_components = []
    inaccessible_components = []
    no_path_components = []
    
    # Get all components
    all_components = []
    for comp_type in stats.get('component_types', {}):
        components = dm.get_components_by_type(comp_type)
        all_components.extend(components)
    
    for component in all_components:
        comp_name = component['name']
        info = dm.get_component_info(comp_name)
        
        if not info:
            continue
            
        file_path = info.get('path', '')
        
        if not file_path:
            no_path_count += 1
            no_path_components.append(comp_name)
            continue
        
        # Resolve absolute path
        if not os.path.isabs(file_path) and code_base:
            absolute_path = os.path.join(code_base, file_path)
        else:
            absolute_path = file_path
        
        if os.path.exists(absolute_path):
            accessible_count += 1
            accessible_components.append({
                "name": comp_name,
                "path": absolute_path,
                "type": info.get('type', 'Unknown')
            })
        else:
            inaccessible_count += 1
            inaccessible_components.append({
                "name": comp_name,
                "path": absolute_path,
                "type": info.get('type', 'Unknown')
            })
    
    return json.dumps({
        "validation_summary": {
            "total_components": len(all_components),
            "accessible_files": accessible_count,
            "inaccessible_files": inaccessible_count,
            "no_path_registered": no_path_count,
            "code_base_configured": bool(code_base),
            "code_base_path": code_base
        },
        "accessible_components": accessible_components[:10],  # Limit to first 10
        "inaccessible_components": inaccessible_components,
        "no_path_components": no_path_components,
        "note": "Source files can be accessed using read_component_source tool when accessible_files > 0"
    }, indent=2)


# Create MCP tools
read_component_source_tool = Tool.from_function(
    fn=read_component_source,
    name="read_component_source",
    description="Read the source code content of a mainframe component. The file path is resolved using the component's registered path and the ATX_MF_CODE_BASE environment variable. Returns the actual source code content that can be analyzed."
)

get_component_source_info_tool = Tool.from_function(
    fn=get_component_source_info,
    name="get_component_source_info",
    description="Get component information with explicit source code access details. This tool confirms that source files are accessible via the ATX_MF_CODE_BASE environment variable and provides file accessibility status."
)

list_component_directory_tool = Tool.from_function(
    fn=list_component_directory,
    name="list_component_directory",
    description="List files in the directory containing a mainframe component. Useful for discovering related files, includes, copybooks, or documentation in the same directory."
)

validate_source_access_tool = Tool.from_function(
    fn=validate_source_access,
    name="validate_source_access",
    description="Validate that source code files are accessible for all components. Provides a summary of which components have accessible source files and identifies any missing files."
)
