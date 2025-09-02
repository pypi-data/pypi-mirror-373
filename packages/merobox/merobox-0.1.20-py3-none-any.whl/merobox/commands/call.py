"""
Call command - Execute function calls using JSON-RPC client.
"""

import click
import asyncio
import sys
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich import box
from merobox.commands.utils import get_node_rpc_url
from merobox.commands.manager import CalimeroManager

console = Console()


async def call_function(
    rpc_url: str,
    context_id: str,
    function_name: str,
    args: Optional[Dict[str, Any]] = None,
    executor_public_key: Optional[str] = None,
) -> dict:
    """Execute a function call using the admin API.

    Args:
        rpc_url: The admin API URL of the Calimero node.
        context_id: The ID of the context to execute in.
        function_name: The function to call.
        args: Optional arguments for the function call.

    Returns:
        The execution result.
    """
    try:
        # Import the admin client
        from calimero import AdminClient

        # Create admin client using the admin API URL
        client = AdminClient(rpc_url)

        # Try to use JSON-RPC endpoint on the admin port
        # The endpoint might be /jsonrpc instead of /jsonrpc/dev
        import aiohttp

        url = f"{rpc_url}/jsonrpc"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "execute",
            "params": {
                "contextId": context_id,
                "method": function_name,
                "argsJson": args or {},
                "timeout": 1000,
            },
        }

        # Add executorPublicKey if provided
        if executor_public_key:
            payload["params"]["executorPublicKey"] = executor_public_key

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result_data = await response.json()
                    return {"success": True, "data": result_data}
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                    }

        return result

    except Exception as e:
        return {"success": False, "error": str(e)}


def run_async_function(func, *args, **kwargs):
    """Helper function to run async functions in sync context."""
    try:
        return asyncio.run(func(*args, **kwargs))
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return None


@click.command()
@click.option("--node", required=True, help="Node name to execute the function on")
@click.option("--context-id", required=True, help="Context ID to execute in")
@click.option("--function", required=True, help="Function name to call")
@click.option("--args", help="JSON string of arguments for the function call")
def call(node: str, context_id: str, function: str, args: str = None):
    """Execute function calls."""

    # Initialize manager and get RPC URL from node name
    manager = CalimeroManager()
    rpc_url = get_node_rpc_url(node, manager)

    console.print(f"[blue]Using RPC endpoint: {rpc_url}[/blue]")

    # Parse args if provided
    parsed_args = None
    if args:
        try:
            import json

            parsed_args = json.loads(args)
        except json.JSONDecodeError as e:
            console.print(f"[red]Error parsing JSON arguments: {str(e)}[/red]")
            return

    # Execute the function call
    result = run_async_function(
        call_function, rpc_url, context_id, function, parsed_args
    )

    if result:
        if result.get("success"):
            console.print(
                Panel(
                    f"[green]Function call successful![/green]\n\n"
                    f"Function: {function}\n"
                    f"Context: {context_id}\n"
                    f"Node: {node}\n"
                    f"Result: {result.get('data', 'No data returned')}",
                    title="Function Call Result",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[red]Function call failed![/red]\n\n"
                    f"Function: {function}\n"
                    f"Context: {context_id}\n"
                    f"Node: {node}\n"
                    f"Error: {result.get('error', 'Unknown error')}",
                    title="Function Call Error",
                    border_style="red",
                )
            )
    else:
        console.print("[red]Failed to execute function call[/red]")


if __name__ == "__main__":
    call()
