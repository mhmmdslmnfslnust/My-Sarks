import sys
from cli import run_cli
from gui import run_gui


if __name__ == "__main__":
    # Check if the user wants to use GUI or CLI
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--cli":
        run_cli()
    else:
        # Default to GUI if no arguments or if anything other than --cli is specified
        run_gui()
