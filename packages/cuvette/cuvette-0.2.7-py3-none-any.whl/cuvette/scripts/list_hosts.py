import argparse
import json
import subprocess
from typing import List

from rich.console import Console
from rich.table import Table


def get_node_hostnames() -> List[str]:
    """Get a sorted list of all hostnames from beaker nodes."""
    try:
        # Run beaker CLI command to get node list
        cmd = ["beaker", "node", "list", "--format", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            console = Console()
            console.print(f"Failed to get node list: {result.stderr}", style="red")
            return []

        # Parse JSON output
        nodes_data = json.loads(result.stdout)

        # Extract hostnames
        hostnames = []
        for node in nodes_data:
            if "hostname" in node and node["hostname"]:
                hostnames.append(node["hostname"])

        # Sort hostnames
        hostnames.sort()
        return hostnames

    except json.JSONDecodeError as e:
        console = Console()
        console.print(f"Failed to parse JSON output: {e}", style="red")
        return []
    except Exception as e:
        console = Console()
        console.print(f"Error getting node hostnames: {e}", style="red")
        return []


def display_hostnames_table(hostnames: List[str]):
    """Display hostnames in a multi-column table format."""
    console = Console()
    table = Table(header_style="bold", box=None)
    
    num_cols = min(4, len(hostnames))
    for i in range(num_cols):
        table.add_column(f"", style="cyan")
    
    for i in range(0, len(hostnames), num_cols):
        row = []
        for j in range(num_cols):
            if i + j < len(hostnames):
                row.append(hostnames[i + j])
            else:
                row.append("")
        table.add_row(*row)
    
    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="List all hostnames from beaker nodes in sorted order."
    )
    args = parser.parse_args()

    hostnames = get_node_hostnames()
    
    display_hostnames_table(hostnames)


if __name__ == "__main__":
    main()
