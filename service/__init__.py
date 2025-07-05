
from pathlib import Path
import logging
import sys

import click
from .server import ser

@click.command()
@click.option("--repository", "-r", type=Path, help="Git repository path")
@click.option("-v", "--verbose", count=True)
def main(repository: Path | None , verbose : bool) -> None:
    """MCP Git Server - Git functionality for MCP"""
    import asyncio

    print("Starting MCP Git Server...")

    logging.basicConfig(filename="C:\Albert\Learn\Log\workflow\server.log"  ,level=logging.DEBUG)

    try:
        asyncio.run(ser(repository))
    except Exception as e:
        logging.exception("An error occurred while running the MCP server:")
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
