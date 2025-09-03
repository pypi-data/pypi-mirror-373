"""
AWS Transform for mainframe (ATX) - Mainframe Dependency Manager

A comprehensive tool for managing mainframe component dependencies and relationships.
Can be used as both an MCP server and a Python library for analyzing mainframe codebases.

This package provides tools for analyzing, tracking, and managing dependencies between mainframe
components such as COBOL programs, JCL jobs, and copybooks. It integrates with AWS Transform
for mainframe analysis outputs to provide advanced dependency analysis capabilities.

Usage as MCP Server:
    Set ATX_MF_DEPENDENCIES_FILE and ATX_MF_CODE_BASE environment variables
    and run: atx-mainframe-dependency-manager

Usage as Python Library:
    from atx_mainframe_dependency_manager import DependencyManager
    dm = DependencyManager()
    dm.load_dependencies("/path/to/dependencies.json")
"""

__version__ = "0.1.5"
__author__ = "Arunkumar Selvam"
__email__ = "aruninfy123@gmail.com"

from .dependency_manager import DependencyManager
from .server import main

__all__ = ["DependencyManager", "main"]
