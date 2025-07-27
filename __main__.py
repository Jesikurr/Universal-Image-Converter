import sys

def is_cli():
    return len(sys.argv) > 1 and any(arg.startswith("--") or arg.startswith("-") for arg in sys.argv[1:])

if __name__ == "__main__":
    if is_cli():
        from cli import main as cli_main
        cli_main()
    else:
        from gui import ImageConverterApp
        app = ImageConverterApp()
        app.run()