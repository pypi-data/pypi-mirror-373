import json
import os
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp.tools import Tool
from ..dependency_manager import get_dependency_manager


def load_dependencies(dependencies_file: str) -> str:
    """Load dependencies from a JSON file.
    
    Args:
        dependencies_file: Path to the JSON file containing dependencies
        
    Returns:
        Status message indicating success or failure
    """
    if not os.path.exists(dependencies_file):
        return f"Error: Dependencies file '{dependencies_file}' not found"
    
    try:
        dm = get_dependency_manager(dependencies_file)
        stats = dm.get_statistics()
        code_base = os.getenv('ATX_MF_CODE_BASE', 'Not set')
        return f"Successfully loaded {stats['total_components']} components from {dependencies_file}\nCode base path: {code_base}"
    except Exception as e:
        return f"Error loading dependencies: {str(e)}"


def get_configuration_info() -> str:
    """Get current configuration information including environment variables.
    
    Returns:
        Configuration information
    """
    dependencies_file = os.getenv('ATX_MF_DEPENDENCIES_FILE', 'Not set')
    code_base = os.getenv('ATX_MF_CODE_BASE', 'Not set')
    
    config_info = {
        "environment_variables": {
            "ATX_MF_DEPENDENCIES_FILE": dependencies_file,
            "ATX_MF_CODE_BASE": code_base
        },
        "dependencies_file_exists": os.path.exists(dependencies_file) if dependencies_file != 'Not set' else False,
        "code_base_exists": os.path.exists(code_base) if code_base != 'Not set' else False
    }
    
    # Add dependency manager status
    dm = get_dependency_manager()
    stats = dm.get_statistics()
    config_info["loaded_components"] = stats['total_components']
    
    return json.dumps(config_info, indent=2)


def get_component_dependencies(component_name: str) -> str:
    """Get direct dependencies of a component.
    
    Args:
        component_name: Name of the component
        
    Returns:
        JSON string of dependencies or error message
    """
    dm = get_dependency_manager()
    dependencies = dm.get_dependencies(component_name)
    
    if not dependencies:
        return f"No dependencies found for component '{component_name}'"
    
    return json.dumps({
        "component": component_name,
        "dependencies": dependencies,
        "count": len(dependencies)
    }, indent=2)


def get_component_dependents(component_name: str) -> str:
    """Get direct dependents of a component.
    
    Args:
        component_name: Name of the component
        
    Returns:
        JSON string of dependents or error message
    """
    dm = get_dependency_manager()
    dependents = dm.get_dependents(component_name)
    
    if not dependents:
        return f"No dependents found for component '{component_name}'"
    
    return json.dumps({
        "component": component_name,
        "dependents": dependents,
        "count": len(dependents)
    }, indent=2)


def get_recursive_dependencies(component_name: str) -> str:
    """Get all dependencies recursively for a component.
    
    Args:
        component_name: Name of the component
        
    Returns:
        JSON string of all dependencies or error message
    """
    dm = get_dependency_manager()
    dependencies = dm.get_recursive_dependencies(component_name)
    
    if not dependencies:
        return f"No recursive dependencies found for component '{component_name}'"
    
    # Remove duplicates while preserving order
    seen = set()
    unique_dependencies = []
    for dep in dependencies:
        dep_key = (dep['name'], dep['type'])
        if dep_key not in seen:
            seen.add(dep_key)
            unique_dependencies.append(dep)
    
    return json.dumps({
        "component": component_name,
        "recursive_dependencies": unique_dependencies,
        "count": len(unique_dependencies)
    }, indent=2)


def get_recursive_dependents(component_name: str) -> str:
    """Get all dependents recursively for a component.
    
    Args:
        component_name: Name of the component
        
    Returns:
        JSON string of all dependents or error message
    """
    dm = get_dependency_manager()
    dependents = dm.get_recursive_dependents(component_name)
    
    if not dependents:
        return f"No recursive dependents found for component '{component_name}'"
    
    # Remove duplicates while preserving order
    seen = set()
    unique_dependents = []
    for dep in dependents:
        dep_key = (dep['name'], dep['type'])
        if dep_key not in seen:
            seen.add(dep_key)
            unique_dependents.append(dep)
    
    return json.dumps({
        "component": component_name,
        "recursive_dependents": unique_dependents,
        "count": len(unique_dependents)
    }, indent=2)


def get_component_info(component_name: str) -> str:
    """Get detailed information about a component.
    
    Args:
        component_name: Name of the component
        
    Returns:
        JSON string of component information or error message
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
        
        if os.path.exists(absolute_path):
            result['source_access_note'] = "Source code can be accessed using read_component_source tool or by reading the file directly"
        else:
            result['source_access_note'] = "Source file not found at the specified path"
    else:
        result['absolute_path'] = None
        result['file_accessible'] = False
        result['source_access_note'] = "No file path registered for this component"
    
    return json.dumps(result, indent=2)


def find_component_by_path(file_path: str) -> str:
    """Find a component by its file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Component name or error message
    """
    dm = get_dependency_manager()
    component_name = dm.find_component_by_path(file_path)
    
    if not component_name:
        return f"No component found for path '{file_path}'"
    
    return f"Component '{component_name}' found for path '{file_path}'"


def get_components_by_type(component_type: str) -> str:
    """Get all components of a specific type.
    
    Args:
        component_type: Type of components to find (e.g., 'COB', 'JCL', 'CPY')
        
    Returns:
        JSON string of components or error message
    """
    dm = get_dependency_manager()
    components = dm.get_components_by_type(component_type)
    
    if not components:
        return f"No components found of type '{component_type}'"
    
    return json.dumps({
        "component_type": component_type,
        "components": components,
        "count": len(components)
    }, indent=2)


def get_orphaned_components() -> str:
    """Get components with no dependencies and no dependents.
    
    Returns:
        JSON string of orphaned components
    """
    dm = get_dependency_manager()
    orphaned = dm.get_orphaned_components()
    
    if not orphaned:
        return "No orphaned components found"
    
    return json.dumps({
        "orphaned_components": orphaned,
        "count": len(orphaned)
    }, indent=2)


def get_dependency_statistics() -> str:
    """Get statistics about the dependency graph.
    
    Returns:
        JSON string of statistics
    """
    dm = get_dependency_manager()
    stats = dm.get_statistics()
    
    return json.dumps(stats, indent=2)


def add_component(name: str, component_type: str = "Unknown", path: str = "") -> str:
    """Add a new component to the dependency graph.
    
    Args:
        name: Name of the component
        component_type: Type of the component (default: "Unknown")
        path: Path to the component file (default: "")
        
    Returns:
        Success or error message
    """
    dm = get_dependency_manager()
    
    try:
        dm.add_component(name, component_type, path)
        return f"Successfully added component '{name}' of type '{component_type}'"
    except Exception as e:
        return f"Error adding component: {str(e)}"


def add_dependency(source_name: str, target_name: str, dependency_type: str = "Unknown") -> str:
    """Add a dependency between two components.
    
    Args:
        source_name: Name of the source component
        target_name: Name of the target component (dependency)
        dependency_type: Type of dependency (default: "Unknown")
        
    Returns:
        Success or error message
    """
    dm = get_dependency_manager()
    
    success = dm.add_dependency(source_name, target_name, dependency_type)
    if success:
        return f"Successfully added dependency from '{source_name}' to '{target_name}'"
    else:
        return f"Failed to add dependency from '{source_name}' to '{target_name}'"


def save_dependencies(output_file: str) -> str:
    """Save dependencies to a JSON file.
    
    Args:
        output_file: Path to the output JSON file
        
    Returns:
        Success or error message
    """
    dm = get_dependency_manager()
    
    try:
        dm.save_dependencies(output_file)
        return f"Successfully saved dependencies to '{output_file}'"
    except Exception as e:
        return f"Error saving dependencies: {str(e)}"


# Create MCP tools
load_dependencies_tool = Tool.from_function(
    fn=load_dependencies,
    name="load_dependencies",
    description="Load mainframe component dependencies from a JSON file. This initializes the dependency manager with the provided data."
)

get_configuration_info_tool = Tool.from_function(
    fn=get_configuration_info,
    name="get_configuration_info",
    description="Get current configuration information including environment variables (ATX_MF_DEPENDENCIES_FILE, ATX_MF_CODE_BASE) and dependency manager status."
)

get_component_dependencies_tool = Tool.from_function(
    fn=get_component_dependencies,
    name="get_component_dependencies",
    description="Get the direct dependencies of a specific mainframe component. Returns a list of components that this component depends on."
)

get_component_dependents_tool = Tool.from_function(
    fn=get_component_dependents,
    name="get_component_dependents",
    description="Get the direct dependents of a specific mainframe component. Returns a list of components that depend on this component."
)

get_recursive_dependencies_tool = Tool.from_function(
    fn=get_recursive_dependencies,
    name="get_recursive_dependencies",
    description="Get all dependencies recursively for a mainframe component. This includes dependencies of dependencies, providing a complete dependency tree."
)

get_recursive_dependents_tool = Tool.from_function(
    fn=get_recursive_dependents,
    name="get_recursive_dependents",
    description="Get all dependents recursively for a mainframe component. This includes dependents of dependents, showing the complete impact tree."
)

get_component_info_tool = Tool.from_function(
    fn=get_component_info,
    name="get_component_info",
    description="Get detailed information about a specific mainframe component including its type, path, dependencies, and dependents. The returned path can be used to access the actual source code file using standard file reading tools or the read_component_source tool."
)

find_component_by_path_tool = Tool.from_function(
    fn=find_component_by_path,
    name="find_component_by_path",
    description="Find a mainframe component by its file path. Useful for identifying which component corresponds to a specific file. The file path can be absolute or relative to ATX_MF_CODE_BASE environment variable."
)

get_components_by_type_tool = Tool.from_function(
    fn=get_components_by_type,
    name="get_components_by_type",
    description="Get all mainframe components of a specific type (e.g., 'COB' for COBOL programs, 'JCL' for job control language, 'CPY' for copybooks)."
)

get_orphaned_components_tool = Tool.from_function(
    fn=get_orphaned_components,
    name="get_orphaned_components",
    description="Get mainframe components that have no dependencies and no dependents. These are isolated components that might be unused."
)

get_dependency_statistics_tool = Tool.from_function(
    fn=get_dependency_statistics,
    name="get_dependency_statistics",
    description="Get comprehensive statistics about the mainframe dependency graph including component counts, types, and complexity metrics."
)

add_component_tool = Tool.from_function(
    fn=add_component,
    name="add_component",
    description="Add a new mainframe component to the dependency graph. Specify the component name, type, and optional file path."
)

add_dependency_tool = Tool.from_function(
    fn=add_dependency,
    name="add_dependency",
    description="Add a dependency relationship between two mainframe components. The source component will depend on the target component."
)

save_dependencies_tool = Tool.from_function(
    fn=save_dependencies,
    name="save_dependencies",
    description="Save the current dependency graph to a JSON file. This persists any changes made to the dependency data."
)
