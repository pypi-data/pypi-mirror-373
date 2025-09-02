"""
Shared utilities for Calimero CLI commands.
"""

import os
import sys
import time
import asyncio
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from merobox.commands.manager import CalimeroManager

console = Console()


def get_node_rpc_url(node_name: str, manager: CalimeroManager) -> str:
    """Get the RPC URL for a specific node."""
    try:
        container = manager.client.containers.get(node_name)

        # Get port mappings from container attributes
        if container.attrs.get("NetworkSettings", {}).get("Ports"):
            port_mappings = container.attrs["NetworkSettings"]["Ports"]

            for container_port, host_bindings in port_mappings.items():
                if host_bindings and container_port == "2528/tcp":
                    for binding in host_bindings:
                        if "HostPort" in binding:
                            host_port = binding["HostPort"]
                            return f"http://localhost:{host_port}"

        # Fallback to default
        return "http://localhost:2528"

    except Exception:
        return "http://localhost:2528"


def check_node_running(node: str, manager: CalimeroManager) -> None:
    """Check if a node is running and exit if not."""
    try:
        container = manager.client.containers.get(node)
        if container.status != "running":
            console.print(f"[red]Node {node} is not running[/red]")
            sys.exit(1)
    except Exception:
        console.print(f"[red]Node {node} not found[/red]")
        sys.exit(1)


def run_async_function(func, *args) -> Dict[str, Any]:
    """Helper to run async functions in sync context."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(func(*args))
        loop.close()
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_generic_table(
    title: str, columns: List[tuple], data: List[Dict[str, Any]]
) -> Table:
    """Create a generic table with specified columns and data."""
    table = Table(title=title, box=box.ROUNDED)

    for col_name, col_style in columns:
        table.add_column(col_name, style=col_style)

    for row_data in data:
        row_values = []
        for col_name, _ in columns:
            row_values.append(row_data.get(col_name, "Unknown"))
        table.add_row(*row_values)

    return table


def extract_nested_data(response_data: Dict[str, Any], *keys) -> Any:
    """Extract data from nested dictionary using multiple possible key paths."""
    if not isinstance(response_data, dict):
        return None

    # Try direct key access first
    for key in keys:
        if key in response_data:
            return response_data[key]

    # Try nested data structure
    if "data" in response_data:
        data = response_data["data"]
        if isinstance(data, dict):
            for key in keys:
                if key in data:
                    return data[key]

    return None


def validate_port(port_str: str, port_name: str) -> int:
    """Validate and convert port string to integer."""
    try:
        port = int(port_str)
        if port < 1 or port > 65535:
            raise ValueError(f"Port must be between 1 and 65535")
        return port
    except ValueError as e:
        console.print(f"[red]Error: Invalid {port_name} '{port_str}'. {str(e)}[/red]")
        sys.exit(1)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary with a default fallback."""
    return dictionary.get(key, default) if isinstance(dictionary, dict) else default
