#!/usr/bin/env python3
"""
Test script to verify the new source code access tools work correctly.
"""

import os
import json
import tempfile
import shutil
from atx_mainframe_dependency_manager.tools.source_code_tools import (
    read_component_source,
    get_component_source_info,
    list_component_directory,
    validate_source_access
)
from atx_mainframe_dependency_manager.tools.dependency_tools import (
    load_dependencies,
    get_component_info
)

def create_test_environment():
    """Create a test environment with sample files and dependencies."""
    # Create temporary directory structure
    temp_dir = tempfile.mkdtemp()
    cobol_dir = os.path.join(temp_dir, "cobol")
    copybook_dir = os.path.join(temp_dir, "copybooks")
    
    os.makedirs(cobol_dir)
    os.makedirs(copybook_dir)
    
    # Create sample COBOL program
    payroll_content = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. PAYROLL.
       
       ENVIRONMENT DIVISION.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       COPY EMPLOYEE.
       COPY SALARY.
       
       PROCEDURE DIVISION.
       MAIN-LOGIC.
           DISPLAY 'Processing payroll...'.
           STOP RUN.
"""
    
    with open(os.path.join(cobol_dir, "PAYROLL.cob"), "w") as f:
        f.write(payroll_content)
    
    # Create sample copybooks
    employee_content = """       01  EMPLOYEE-RECORD.
           05  EMP-ID          PIC 9(6).
           05  EMP-NAME        PIC X(30).
           05  EMP-DEPT        PIC X(10).
"""
    
    salary_content = """       01  SALARY-RECORD.
           05  SAL-EMP-ID      PIC 9(6).
           05  SAL-AMOUNT      PIC 9(8)V99.
           05  SAL-CURRENCY    PIC X(3).
"""
    
    with open(os.path.join(copybook_dir, "EMPLOYEE.cpy"), "w") as f:
        f.write(employee_content)
    
    with open(os.path.join(copybook_dir, "SALARY.cpy"), "w") as f:
        f.write(salary_content)
    
    # Create dependencies JSON
    dependencies = [
        {
            "name": "PAYROLL",
            "type": "COB",
            "path": "cobol/PAYROLL.cob",
            "dependencies": [
                {"name": "EMPLOYEE", "dependencyType": "COPY"},
                {"name": "SALARY", "dependencyType": "COPY"}
            ]
        },
        {
            "name": "EMPLOYEE",
            "type": "CPY",
            "path": "copybooks/EMPLOYEE.cpy",
            "dependencies": []
        },
        {
            "name": "SALARY",
            "type": "CPY",
            "path": "copybooks/SALARY.cpy",
            "dependencies": []
        }
    ]
    
    deps_file = os.path.join(temp_dir, "dependencies.json")
    with open(deps_file, "w") as f:
        json.dump(dependencies, f, indent=2)
    
    return temp_dir, deps_file

def test_source_access_tools():
    """Test the new source access tools."""
    print("Creating test environment...")
    temp_dir, deps_file = create_test_environment()
    
    # Store original environment variables
    original_code_base = os.environ.get('ATX_MF_CODE_BASE')
    original_deps_file = os.environ.get('ATX_MF_DEPENDENCIES_FILE')
    
    # Set environment variables
    os.environ['ATX_MF_CODE_BASE'] = temp_dir
    os.environ['ATX_MF_DEPENDENCIES_FILE'] = deps_file
    
    try:
        print(f"Test directory: {temp_dir}")
        print(f"Dependencies file: {deps_file}")
        
        # Load dependencies
        print("\n1. Loading dependencies...")
        result = load_dependencies(deps_file)
        print(result)
        
        # Test get_component_info (enhanced version)
        print("\n2. Testing enhanced get_component_info...")
        result = get_component_info("PAYROLL")
        print(result)
        
        # Test get_component_source_info
        print("\n3. Testing get_component_source_info...")
        result = get_component_source_info("PAYROLL")
        print(result)
        
        # Test read_component_source
        print("\n4. Testing read_component_source...")
        result = read_component_source("PAYROLL")
        result_data = json.loads(result)
        print(f"Component: {result_data['component_name']}")
        print(f"File path: {result_data['file_path']}")
        print(f"File size: {result_data['file_size']} bytes")
        print(f"Line count: {result_data['line_count']}")
        print("Content preview:")
        print(result_data['content'][:200] + "..." if len(result_data['content']) > 200 else result_data['content'])
        
        # Test list_component_directory
        print("\n5. Testing list_component_directory...")
        result = list_component_directory("PAYROLL")
        print(result)
        
        # Test validate_source_access
        print("\n6. Testing validate_source_access...")
        result = validate_source_access()
        result_data = json.loads(result)
        print(f"Total components: {result_data['validation_summary']['total_components']}")
        print(f"Accessible files: {result_data['validation_summary']['accessible_files']}")
        print(f"Inaccessible files: {result_data['validation_summary']['inaccessible_files']}")
        print(f"Code base configured: {result_data['validation_summary']['code_base_configured']}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Restore original environment variables
        if original_code_base is not None:
            os.environ['ATX_MF_CODE_BASE'] = original_code_base
        elif 'ATX_MF_CODE_BASE' in os.environ:
            del os.environ['ATX_MF_CODE_BASE']
            
        if original_deps_file is not None:
            os.environ['ATX_MF_DEPENDENCIES_FILE'] = original_deps_file
        elif 'ATX_MF_DEPENDENCIES_FILE' in os.environ:
            del os.environ['ATX_MF_DEPENDENCIES_FILE']
        
        # Clean up
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up test directory: {temp_dir}")

if __name__ == "__main__":
    test_source_access_tools()
