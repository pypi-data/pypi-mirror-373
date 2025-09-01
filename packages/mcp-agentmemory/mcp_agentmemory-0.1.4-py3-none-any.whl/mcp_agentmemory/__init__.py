import click
from pathlib import Path
from .server import mcp, manager, MEMORY_FILE, MEMORY_LOG


@click.command()
@click.option(
    "--memory-file-path",
    "-f",
    default="~/.mcp/",
    help="Path to the memory file",
)
def main(memory_file_path: str) -> None:
    """Memory Graph MCP Server for Python Development Insights"""

    # Storage configuration - moved from server.py
    memory_file_path = Path(memory_file_path).expanduser()

    # Configure the manager with the specified paths
    manager.snapshot_path = memory_file_path / MEMORY_FILE
    manager.log_path = memory_file_path / MEMORY_LOG

    # Start the server
    mcp.run()


if __name__ == "__main__":
    main()
