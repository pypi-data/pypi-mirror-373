#!/usr/bin/env python3
# dependency_manager.py - Mainframe dependency manager for MCP

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Set

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S.%f',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'dependency_manager.log'), mode='w')
    ]
)
logger = logging.getLogger(__name__)

class DependencyManager:
    """Manage dependencies between mainframe components"""

    def __init__(self, dependencies_file: Optional[str] = None):
        """Initialize the dependency manager.

        Args:
            dependencies_file: Path to the JSON file containing dependencies.
                              If not provided, will check ATX_MF_DEPENDENCIES_FILE environment variable.
        """
        self.dependencies: List[Dict[str, Any]] = []
        self.dependency_graph: Dict[str, Dict[str, Any]] = {}
        self.code_base_path: str = os.getenv('ATX_MF_CODE_BASE', '')

        # Determine dependencies file path
        if not dependencies_file:
            dependencies_file = os.getenv('ATX_MF_DEPENDENCIES_FILE')
        
        if dependencies_file and os.path.exists(dependencies_file):
            self.load_dependencies(dependencies_file)
            self.build_dependency_graph()
        elif dependencies_file:
            logger.warning(f"Dependencies file '{dependencies_file}' not found")
        else:
            logger.info("No dependencies file specified. Use load_dependencies() to load data or set ATX_MF_DEPENDENCIES_FILE environment variable.")

    def load_dependencies(self, dependencies_file: str) -> None:
        """Load dependencies from JSON file.

        Args:
            dependencies_file: Path to the JSON file containing dependencies
        """
        try:
            with open(dependencies_file, 'r', encoding='utf-8') as f:
                self.dependencies = json.load(f)
            logger.info(f"Loaded {len(self.dependencies)} components from dependency file")
        except Exception as e:
            logger.error(f"Failed to load dependencies from {dependencies_file}: {e}")

    def build_dependency_graph(self) -> None:
        """Build a dependency graph from loaded dependencies."""
        # Build forward dependency graph (what depends on what)
        self.dependency_graph = {}

        # Initialize graph with all components
        for component in self.dependencies:
            name = component.get('name')
            if name:
                self.dependency_graph[name] = {
                    'type': component.get('type', 'Unknown'),
                    'path': component.get('path', ''),
                    'dependents': [],  # Components that depend on this
                    'dependencies': []  # Components this depends on
                }

        # Add dependency relationships
        for component in self.dependencies:
            comp_name = component.get('name')
            if not comp_name:
                continue

            # Add this component's dependencies
            for dependency in component.get('dependencies', []):
                dep_name = dependency.get('name')
                dep_type = dependency.get('dependencyType', 'Unknown')

                if dep_name and dep_name in self.dependency_graph:
                    # Add to this component's dependencies
                    self.dependency_graph[comp_name]['dependencies'].append({
                        'name': dep_name,
                        'type': dep_type
                    })

                    # Add this component to dependent's dependents
                    self.dependency_graph[dep_name]['dependents'].append({
                        'name': comp_name,
                        'type': dep_type
                    })

        logger.info(f"Built dependency graph with {len(self.dependency_graph)} components")

    def get_dependencies(self, component_name: str) -> List[Dict[str, str]]:
        """Get direct dependencies of a component.

        Args:
            component_name: Name of the component

        Returns:
            List of dependency objects (each with 'name' and 'type')
        """
        if component_name in self.dependency_graph:
            return self.dependency_graph[component_name]['dependencies']
        return []

    def get_dependents(self, component_name: str) -> List[Dict[str, str]]:
        """Get direct dependents of a component.

        Args:
            component_name: Name of the component

        Returns:
            List of dependent objects (each with 'name' and 'type')
        """
        if component_name in self.dependency_graph:
            return self.dependency_graph[component_name]['dependents']
        return []

    def get_recursive_dependencies(self, component_name: str, visited: Optional[Set[str]] = None) -> List[Dict[str, str]]:
        """Get all dependencies recursively.

        Args:
            component_name: Name of the component
            visited: Set of already visited components (for recursion)

        Returns:
            List of all dependencies recursively
        """
        if visited is None:
            visited = set()

        if component_name in visited:
            return []

        visited.add(component_name)
        result = self.get_dependencies(component_name)

        for dependency in self.get_dependencies(component_name):
            dep_name = dependency['name']
            if dep_name not in visited:
                result.extend(self.get_recursive_dependencies(dep_name, visited))

        return result

    def get_recursive_dependents(self, component_name: str, visited: Optional[Set[str]] = None) -> List[Dict[str, str]]:
        """Get all dependents recursively.

        Args:
            component_name: Name of the component
            visited: Set of already visited components (for recursion)

        Returns:
            List of all dependents recursively
        """
        if visited is None:
            visited = set()

        if component_name in visited:
            return []

        visited.add(component_name)
        result = self.get_dependents(component_name)

        for dependent in self.get_dependents(component_name):
            dep_name = dependent['name']
            if dep_name not in visited:
                result.extend(self.get_recursive_dependents(dep_name, visited))

        return result

    def get_component_info(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a component.

        Args:
            component_name: Name of the component

        Returns:
            Component information dictionary or None if not found
        """
        if component_name in self.dependency_graph:
            return self.dependency_graph.get(component_name)
        return None

    def find_component_by_path(self, file_path: str) -> Optional[str]:
        """Find component by path (partial matching for simplicity).

        Args:
            file_path: Path to file (can be absolute or relative to ATX_MF_CODE_BASE)

        Returns:
            Component name or None if not found
        """
        # Convert to Path object for better cross-platform handling
        path_obj = Path(file_path)
        
        # Handle relative paths by prepending code base path
        if self.code_base_path and not path_obj.is_absolute():
            full_path = Path(self.code_base_path) / path_obj
        else:
            full_path = path_obj
            
        basename = full_path.name

        # Try exact name match first
        for name, info in self.dependency_graph.items():
            if name == basename:
                return name

        # Try path match (both full path and basename)
        for name, info in self.dependency_graph.items():
            component_path = info.get('path', '')
            if component_path:
                component_path_obj = Path(component_path)
                
                # Handle relative paths in component data
                if self.code_base_path and not component_path_obj.is_absolute():
                    component_full_path = Path(self.code_base_path) / component_path_obj
                else:
                    component_full_path = component_path_obj
                
                # Check if paths match or if basename is in component path
                if (str(full_path) == str(component_full_path) or 
                    basename in component_path or 
                    basename in component_path_obj.name):
                    return name

        return None

    def add_component(self, name: str, component_type: str = "Unknown", path: str = "") -> None:
        """Add a new component to the dependency graph.

        Args:
            name: Name of the component
            component_type: Type of the component
            path: Path to the component file
        """
        if name in self.dependency_graph:
            logger.warning(f"Component {name} already exists in the dependency graph")
            return

        # Add to dependencies list
        self.dependencies.append({
            'name': name,
            'type': component_type,
            'path': path,
            'dependencies': []
        })

        # Add to dependency graph
        self.dependency_graph[name] = {
            'type': component_type,
            'path': path,
            'dependents': [],
            'dependencies': []
        }

        logger.info(f"Added component {name} to dependency graph")

    def add_dependency(self, source_name: str, target_name: str, dependency_type: str = "Unknown") -> bool:
        """Add a dependency between two components.

        Args:
            source_name: Name of the source component
            target_name: Name of the target component (dependency)
            dependency_type: Type of dependency

        Returns:
            True if successful, False otherwise
        """
        if source_name not in self.dependency_graph:
            logger.error(f"Source component {source_name} not found in dependency graph")
            return False

        if target_name not in self.dependency_graph:
            logger.error(f"Target component {target_name} not found in dependency graph")
            return False

        # Check if dependency already exists
        for dep in self.dependency_graph[source_name]['dependencies']:
            if dep['name'] == target_name:
                logger.warning(f"Dependency from {source_name} to {target_name} already exists")
                return True

        # Add dependency to source component
        self.dependency_graph[source_name]['dependencies'].append({
            'name': target_name,
            'type': dependency_type
        })

        # Add dependent to target component
        self.dependency_graph[target_name]['dependents'].append({
            'name': source_name,
            'type': dependency_type
        })

        # Update dependencies list
        for component in self.dependencies:
            if component.get('name') == source_name:
                component.setdefault('dependencies', []).append({
                    'name': target_name,
                    'dependencyType': dependency_type
                })
                break

        logger.info(f"Added dependency from {source_name} to {target_name}")
        return True

    def save_dependencies(self, output_file: str) -> None:
        """Save dependencies to a JSON file.

        Args:
            output_file: Path to the output JSON file
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.dependencies, f, indent=2)
            logger.info(f"Saved {len(self.dependencies)} components to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save dependencies to {output_file}: {e}")

    def get_orphaned_components(self) -> List[str]:
        """Get components with no dependencies and no dependents.

        Returns:
            List of orphaned component names
        """
        orphaned = []

        for name, info in self.dependency_graph.items():
            if not info['dependencies'] and not info['dependents']:
                orphaned.append(name)

        return orphaned

    def get_components_by_type(self, component_type: str) -> List[Dict[str, Any]]:
        """Find all components of a specific type.

        Args:
            component_type: Type of components to find (e.g., 'COB', 'JCL', 'CPY')

        Returns:
            List of components matching the specified type
        """
        results = []

        for name, info in self.dependency_graph.items():
            if info['type'] == component_type:
                # Include the component name in the result
                component_info = info.copy()
                component_info['name'] = name
                results.append(component_info)

        logger.info(f"Found {len(results)} components of type '{component_type}'")
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the dependency graph.

        Returns:
            Dictionary of statistics
        """
        component_types = {}
        max_dependencies = 0
        max_dependents = 0
        max_dependencies_component = ""
        max_dependents_component = ""

        for name, info in self.dependency_graph.items():
            component_type = info['type']
            component_types[component_type] = component_types.get(component_type, 0) + 1

            num_dependencies = len(info['dependencies'])
            num_dependents = len(info['dependents'])

            if num_dependencies > max_dependencies:
                max_dependencies = num_dependencies
                max_dependencies_component = name

            if num_dependents > max_dependents:
                max_dependents = num_dependents
                max_dependents_component = name

        return {
            'total_components': len(self.dependency_graph),
            'component_types': component_types,
            'max_dependencies': max_dependencies,
            'max_dependencies_component': max_dependencies_component,
            'max_dependents': max_dependents,
            'max_dependents_component': max_dependents_component,
            'orphaned_components': len(self.get_orphaned_components())
        }

# Global instance for MCP tools
_dependency_manager_instance: Optional[DependencyManager] = None

def get_dependency_manager(dependencies_file: Optional[str] = None) -> DependencyManager:
    """Get or create the global dependency manager instance."""
    global _dependency_manager_instance
    if _dependency_manager_instance is None:
        _dependency_manager_instance = DependencyManager(dependencies_file)
    return _dependency_manager_instance
