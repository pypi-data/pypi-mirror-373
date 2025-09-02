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

### For MCP Server Usage
No installation needed! The MCP configuration with `uvx` will automatically download and run the package.

### For Python Library Usage
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
      "command": "uvx",
      "args": ["atx-mainframe-dependency-manager"],
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

## Sample Prompts for Mainframe Modernization

Once the MCP server is configured, you can use these prompts to guide your mainframe modernization project:

### 🔍 Discovery & Analysis Phase

#### 1. Get Overall System Overview
"Show me the complete mainframe system statistics and component breakdown to understand the modernization scope"

#### 2. Identify Core Business Programs
"Find all COBOL programs that have the most dependencies and dependents - these are likely our core business logic components"

#### 3. Analyze Transaction Processing Components
"Get detailed information about COTRN00C, COTRN01C, and COTRN02C components including their dependencies and source code to understand the transaction processing flow"

#### 4. Discover Account Management Components
"Show me all components related to account management (COACTUPC, COACTVWC, CBACT*) and their dependency relationships"

### 📊 Dependency Analysis for Modernization Planning

#### 5. Find High-Impact Components
"Identify components with the highest number of dependents - these should be modernized first as they impact the most other components"

#### 6. Discover Isolated Components
"Show me all orphaned components that have no dependencies or dependents - these can be modernized independently"

#### 7. Analyze Copybook Dependencies
"Get all CPY (copybook) components and show which COBOL programs depend on them - this will help plan data structure modernization"

#### 8. Map JCL Job Dependencies
"Show me all JCL components and their program dependencies to understand batch processing workflows"

### 🏗️ Microservices Architecture Planning

#### 9. Group Related Components for Service Boundaries
"Analyze the dependency relationships between COBOL programs to identify logical groupings for microservices (e.g., customer management, card management, transaction processing)"

#### 10. Identify Service Interface Points
"Find components that are called by multiple other components - these are candidates for service interfaces in the modernized architecture"

#### 11. Analyze Data Access Patterns
"Show me all components that access the same datasets/files to understand data sharing patterns for database design"

### 🔄 Migration Strategy Development

#### 12. Plan Incremental Migration
"Identify components with the fewest dependencies that can be modernized first in an incremental migration approach"

#### 13. Find Critical Path Components
"Show me the dependency chain from user interface components (COUSR*, COADM*) to data access components to understand the critical modernization path"

#### 14. Analyze Cross-Component Communication
"Get detailed information about how CICS programs call each other to design API interfaces for the modernized system"

### 💾 Data Modernization Planning

#### 15. Map Data Structures
"Read the source code of key copybooks (CVACT01Y, CVCUS01Y, CVTRA05Y) to understand data structures that need to be modernized"

#### 16. Identify File Access Patterns
"Show me all components that read/write to the same files to plan database table design and data access services"

#### 17. Analyze Data Validation Logic
"Get the source code of validation-heavy components like COACTUPC to extract business rules for modern validation services"

### 🧪 Testing Strategy Development

#### 18. Identify Test Boundaries
"Find components that can be tested independently (low coupling) vs. those requiring integration testing (high coupling)"

#### 19. Plan Component Testing Order
"Show me the dependency hierarchy to plan the order of component testing during modernization"

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
