
from pathlib import Path
import logging
import sys

import click
from .server import ser

@click.command()
@click.option("--repository", "-r", type=Path, help="Git repository path")
def main(repository: Path | None) -> None:
    """MCP Git Server - Git functionality for MCP"""
    import asyncio

    print("Starting MCP Git Server...")

    asyncio.run(ser(repository))

if __name__ == "__main__":
    main()
