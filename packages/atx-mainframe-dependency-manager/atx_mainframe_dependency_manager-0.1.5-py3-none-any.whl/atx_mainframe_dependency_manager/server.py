import os
import signal
import sys
import importlib.metadata

from anyio import create_task_group, open_signal_receiver, run
from anyio.abc import CancelScope
from mcp.server.fastmcp import FastMCP

from .tools.dependency_tools import (
    load_dependencies_tool,
    get_configuration_info_tool,
    get_component_dependencies_tool,
    get_component_dependents_tool,
    get_recursive_dependencies_tool,
    get_recursive_dependents_tool,
    get_component_info_tool,
    find_component_by_path_tool,
    get_components_by_type_tool,
    get_orphaned_components_tool,
    get_dependency_statistics_tool,
    add_component_tool,
    add_dependency_tool,
    save_dependencies_tool
)
from .tools.source_code_tools import (
    read_component_source_tool,
    get_component_source_info_tool,
    list_component_directory_tool,
    validate_source_access_tool
)


def get_package_version() -> str:
    """Get the package version."""
    try:
        return importlib.metadata.version("atx-mainframe-dependency-manager")
    except BaseException:
        return "0.1.0"


async def signal_handler(scope: CancelScope):
    """Handle SIGINT and SIGTERM signals asynchronously.

    The anyio.open_signal_receiver returns an async generator that yields
    signal numbers whenever a specified signal is received. The async for
    loop waits for signals and processes them as they arrive.
    
    Note: SIGTERM is not available on Windows, so we only use SIGINT there.
    """
    # Windows doesn't support SIGTERM
    signals_to_handle = [signal.SIGINT]
    if sys.platform != "win32":
        signals_to_handle.append(signal.SIGTERM)
    
    with open_signal_receiver(*signals_to_handle) as signals:
        async for _ in signals:  # Shutting down regardless of the signal type
            print("Shutting down MCP server...")
            # Force immediate exit since MCP blocks on stdio.
            # You can also use scope.cancel(), but it means after Ctrl+C, you need to press another
            # 'Enter' to unblock the stdio.
            os._exit(0)


async def run_server():
    """Run the MCP server with signal handling."""
    mcp = FastMCP(
        name="ATX-MainframeDependencyManager-MCP",
        instructions="A comprehensive MCP server for managing mainframe component dependencies. This server provides tools to analyze, query, and manage dependencies between mainframe components such as COBOL programs, JCL jobs, copybooks, and other mainframe artifacts. Source code files can be accessed directly using the provided file paths and the read_component_source tool.",
    )

    mcp._mcp_server.version = get_package_version()

    # Add all dependency management tools
    dependency_tools = [
        get_configuration_info_tool,
        load_dependencies_tool,
        get_component_dependencies_tool,
        get_component_dependents_tool,
        get_recursive_dependencies_tool,
        get_recursive_dependents_tool,
        get_component_info_tool,
        find_component_by_path_tool,
        get_components_by_type_tool,
        get_orphaned_components_tool,
        get_dependency_statistics_tool,
        add_component_tool,
        add_dependency_tool,
        save_dependencies_tool
    ]
    
    # Add source code access tools
    source_code_tools = [
        read_component_source_tool,
        get_component_source_info_tool,
        list_component_directory_tool,
        validate_source_access_tool
    ]
    
    # Combine all tools
    all_tools = dependency_tools + source_code_tools
    
    for tool in all_tools:
        mcp.add_tool(
            fn=tool.fn,
            name=tool.name,
            description=tool.description,
            annotations=tool.annotations,
        )

    async with create_task_group() as tg:
        tg.start_soon(signal_handler, tg.cancel_scope)
        # proceed with starting the actual application logic
        await mcp.run_stdio_async()


def main():
    """Entry point for the MCP server."""
    run(run_server)
