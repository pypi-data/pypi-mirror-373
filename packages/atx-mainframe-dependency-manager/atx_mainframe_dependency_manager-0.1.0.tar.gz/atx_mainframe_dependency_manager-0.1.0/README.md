# AWS Transform for mainframe (ATX) - Mainframe Dependency Manager

A comprehensive tool for managing mainframe component dependencies and relationships as part of **[AWS Transform for mainframe (ATX)](https://aws.amazon.com/transform/mainframe/)** initiatives. Can be used as both an MCP server and a Python library.

## Overview

This tool extends the **[AWS Transform for mainframe (ATX)](https://aws.amazon.com/transform/mainframe/) analysis workflow** by providing advanced dependency analysis capabilities for mainframe applications. It works with the codebase and dependency graph JSON produced by the ATX analysis step to enable deeper insights and impact analysis.

### ATX Integration Workflow

```
ATX Analysis → dependencies.json + codebase → ATX Mainframe Dependency Manager → Advanced Analysis
```

1. **ATX Analysis**: Analyzes your mainframe codebase and produces `dependencies.json`
2. **ATX Mainframe Dependency Manager**: Uses the same codebase and generated dependency graph for further analysis
3. **Advanced Analysis**: Provides 18+ analysis tools for dependency tracking, impact assessment, and source code access

## Features

- **Dependency Analysis**: Analyze direct and recursive dependencies between mainframe components
- **Impact Assessment**: Understand the impact of changes to specific components  
- **Component Discovery**: Find components by name, type, or file path
- **Orphan Detection**: Identify unused components with no dependencies or dependents
- **Statistics and Reporting**: Get comprehensive statistics about your mainframe codebase
- **Source Code Access**: Read and analyze mainframe source code files
- **Dual Usage**: Works as both MCP server and Python library

## Prerequisites

- **ATX Analysis**: Must be completed first to generate the dependency graph
- **Same Codebase**: Use the identical codebase that was analyzed by ATX
- **Dependencies JSON**: The `dependencies.json` file produced by ATX analysis

## Installation

```bash
pip install atx-mainframe-dependency-manager
```

## Quick Start

### Configuration

Set these environment variables to point to your ATX analysis outputs:

```bash
export ATX_MF_DEPENDENCIES_FILE="/path/to/atx-dependencies.json"
export ATX_MF_CODE_BASE="/path/to/mainframe/codebase"
```

### As MCP Server

```json
{
  "mcpServers": {
    "atx-mainframe-dependency-manager": {
      "command": "atx-mainframe-dependency-manager",
      "env": {
        "ATX_MF_DEPENDENCIES_FILE": "/path/to/atx-dependencies.json",
        "ATX_MF_CODE_BASE": "/path/to/mainframe/codebase"
      }
    }
  }
}
```

### As Python Library

```python
from atx_mainframe_dependency_manager import DependencyManager
import os

# Initialize and load dependencies
dm = DependencyManager()
dm.load_dependencies("/path/to/atx-dependencies.json")
os.environ['ATX_MF_CODE_BASE'] = "/path/to/mainframe/codebase"

# Analyze dependencies
component_info = dm.get_component_info("PAYROLL")
dependencies = dm.get_dependencies("PAYROLL")
stats = dm.get_statistics()
```

## Usage Examples

### Basic Analysis

```python
# Get component information
info = dm.get_component_info("PAYROLL")
print(f"Type: {info['type']}, Path: {info['path']}")

# Find dependencies and dependents
deps = dm.get_dependencies("PAYROLL")
dependents = dm.get_dependents("PAYROLL")

# Get recursive impact analysis
recursive_deps = dm.get_recursive_dependencies("PAYROLL")
recursive_dependents = dm.get_recursive_dependents("PAYROLL")
```

### Component Discovery

```python
# Find components by type
cobol_programs = dm.get_components_by_type("COB")
copybooks = dm.get_components_by_type("CPY")

# Find orphaned components
orphans = dm.get_orphaned_components()

# Search by file path
component = dm.find_component_by_path("/cobol/PAYROLL.cob")

# Get comprehensive statistics
stats = dm.get_statistics()
print(f"Total components: {stats['total_components']}")
```

### Source Code Access

```python
# Read source code content
source_code = dm.read_component_source("PAYROLL")

# Get source file information
source_info = dm.get_component_source_info("PAYROLL")

# Validate source code access
validation_results = dm.validate_source_access()
```

## Analysis Tools Reference

### Component Analysis
- `get_component_info` - Get detailed component information
- `get_component_dependencies` - Get direct dependencies
- `get_recursive_dependencies` - Get complete dependency tree
- `get_component_dependents` - Get components that depend on this one
- `get_recursive_dependents` - Get complete impact tree

### Discovery Tools  
- `get_components_by_type` - List components by type (COB, JCL, CPY, etc.)
- `find_component_by_path` - Find components by file path
- `get_orphaned_components` - Find unused components

### Source Code Tools
- `read_component_source` - Read actual source code content
- `get_component_source_info` - Get source file accessibility details
- `list_component_directory` - List files in component directories
- `validate_source_access` - Check source file accessibility

### System Analysis
- `get_dependency_statistics` - Get comprehensive codebase statistics
- `get_configuration_info` - Get current configuration status

### Management Tools
- `load_dependencies` - Load dependency data from ATX JSON file
- `add_component` - Add new components *(experimental)*
- `add_dependency` - Add new dependency relationships *(experimental)*
- `save_dependencies` - Save current state to JSON file *(experimental)*

**Note**: Management tools marked as *experimental* are available but not fully tested. Use with caution in production environments.

## ATX Dependencies JSON Format

The dependency graph JSON is produced by the ATX analysis step and follows this structure:

```json
[
  {
    "name": "PAYROLL",
    "type": "COB", 
    "path": "/mainframe/cobol/PAYROLL.cob",
    "dependencies": [
      {
        "name": "EMPLOYEE",
        "dependencyType": "COPY"
      }
    ]
  }
]
```

**Note**: This JSON file is automatically generated by ATX analysis - you don't need to create it manually.

## AWS Transform Integration

This tool is designed to work seamlessly with [AWS Transform for mainframe (ATX)](https://aws.amazon.com/transform/mainframe/) workflows:

1. **Run ATX Analysis** on your mainframe codebase
2. **Use the same codebase** and generated `dependencies.json` 
3. **Launch this tool** (as MCP server or library) for advanced dependency analysis
4. **Perform impact analysis** before making changes
5. **Track dependencies** throughout your transformation journey

## License

MIT License - see LICENSE file for details.
