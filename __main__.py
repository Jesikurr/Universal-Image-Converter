"""Main entry point for Universal Image Converter.

Automatically detects whether to launch GUI or CLI mode based on
command-line arguments.
"""

import sys
from typing import Sequence


def is_cli(argv: Sequence[str]) -> bool:
    """Determine if the application should run in CLI mode."""
    return len(argv) > 1 and any(
        arg.startswith("--") or arg.startswith("-") for arg in argv[1:]
    )


if __name__ == "__main__":
    if is_cli(sys.argv):
        from cli import main as cli_main

        raise SystemExit(cli_main())

    from gui import ImageConverterApp

    app = ImageConverterApp()
    app.run()
