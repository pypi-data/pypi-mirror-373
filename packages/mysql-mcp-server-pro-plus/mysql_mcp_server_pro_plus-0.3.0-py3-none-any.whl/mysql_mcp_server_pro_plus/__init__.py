import asyncio
import sys

from . import server


def cli_main():
    """Main entry point for the package."""
    # Handle platform-specific configurations
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    server.main()


# Expose main function for script entry
def main():
    """Main entry point that matches pyproject.toml script configuration."""
    cli_main()


__all__ = ["main", "cli_main", "server"]
