"""Anomaly Surround - Main entry point."""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    args = sys.argv[1:]

    if "--background" in args or "--tray" in args:
        # Run as background tray service
        from tray import run_tray
        run_tray()
    elif "--cli" in args or len(args) > 0 and args[0] not in ("--background", "--tray"):
        # CLI mode - pass remaining args
        sys.argv = [sys.argv[0]] + [a for a in args if a != "--cli"]
        from cli import main as cli_main
        cli_main()
    else:
        # GUI mode (default)
        from gui import run_gui
        run_gui()


if __name__ == "__main__":
    main()
