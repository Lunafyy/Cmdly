import sys
import os


def main():
    """
    Entry point for the CLI application.
    Determines the base path depending on whether the script is running from a PyInstaller bundle or as a normal Python script.
    Modifies the system path to include the 'src' directory, enabling imports of internal modules.
    Delegates execution to the main function of the core.cli module.
    """
    if hasattr(sys, "_MEIPASS"):
        # Running from PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running normally
        base_path = os.path.abspath(os.path.dirname(__file__))

    # Add 'src' folder so imports like 'import core.cli' work
    sys.path.insert(0, os.path.join(base_path, "src"))

    import core.cli

    core.cli.main()


if __name__ == "__main__":
    main()
