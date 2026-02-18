"""Main entry point for Universal Image Converter.

Automatically detects whether to launch GUI or CLI mode based on
command-line arguments.
"""

import sys

def is_cli():
    """Determine if the application should run in CLI mode.
    
    Checks for command-line arguments starting with -- or - to
    identify CLI usage versus GUI mode.
    
    Returns:
        bool: True if CLI mode should be used, False for GUI mode
    """
    return len(sys.argv) > 1 and any(arg.startswith("--") or arg.startswith("-") for arg in sys.argv[1:])

if __name__ == "__main__":
    if is_cli():
        from cli import main as cli_main
        cli_main()
    else:
        from gui import ImageConverterApp
        app = ImageConverterApp()
        app.run()