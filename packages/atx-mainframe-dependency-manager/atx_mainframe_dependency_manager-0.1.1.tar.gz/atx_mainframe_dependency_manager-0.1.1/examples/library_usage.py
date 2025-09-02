#!/usr/bin/env python3
"""
Example: Using ATX Mainframe Dependency Manager as a Python Library

This example shows how to use the package programmatically to analyze
mainframe dependencies from AWS Transform analysis outputs.
"""

import os
from atx_mainframe_dependency_manager import DependencyManager

def main():
    # Initialize the dependency manager
    dm = DependencyManager()
    
    # Load dependencies from ATX analysis output
    dependencies_file = "/path/to/atx-dependencies.json"
    code_base = "/path/to/mainframe/codebase"
    
    try:
        # Load the dependency graph
        dm.load_dependencies(dependencies_file)
        
        # Set code base for source access
        os.environ['ATX_MF_CODE_BASE'] = code_base
        
        print("=== Dependency Analysis Report ===")
        
        # Get overall statistics
        stats = dm.get_statistics()
        print(f"\nTotal Components: {stats['total_components']}")
        print(f"Component Types: {list(stats['component_types'].keys())}")
        
        # Analyze a specific component
        component_name = "PAYROLL"  # Replace with actual component
        
        print(f"\n=== Analysis for {component_name} ===")
        
        # Get component information
        info = dm.get_component_info(component_name)
        if info:
            print(f"Type: {info['type']}")
            print(f"Path: {info['path']}")
            
            # Get dependencies
            deps = dm.get_dependencies(component_name)
            print(f"Direct Dependencies: {len(deps)}")
            for dep in deps:
                print(f"  - {dep['name']} ({dep.get('type', 'Unknown')})")
            
            # Get dependents
            dependents = dm.get_dependents(component_name)
            print(f"Direct Dependents: {len(dependents)}")
            for dep in dependents:
                print(f"  - {dep['name']} ({dep.get('type', 'Unknown')})")
            
            # Get recursive impact
            recursive_deps = dm.get_recursive_dependencies(component_name)
            recursive_dependents = dm.get_recursive_dependents(component_name)
            
            print(f"Total Impact Tree: {len(recursive_deps)} dependencies, {len(recursive_dependents)} dependents")
        
        # Find components by type
        print(f"\n=== Components by Type ===")
        for comp_type in stats['component_types']:
            components = dm.get_components_by_type(comp_type)
            print(f"{comp_type}: {len(components)} components")
        
        # Find orphaned components
        orphans = dm.get_orphaned_components()
        if orphans:
            print(f"\n=== Orphaned Components ===")
            print(f"Found {len(orphans)} orphaned components:")
            for orphan in orphans[:5]:  # Show first 5
                print(f"  - {orphan['name']} ({orphan['type']})")
        
    except FileNotFoundError:
        print(f"Error: Dependencies file not found: {dependencies_file}")
        print("Make sure to run AWS Transform analysis first to generate the dependencies.json file")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
