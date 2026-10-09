"""Command-line entry point for aderrr."""

import argparse

from aderrr import __version__


def main() -> None:
    parser = argparse.ArgumentParser(description="aderrr Python project")
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args()
    print("aderrr is ready. Add your application here.")


if __name__ == "__main__":
    main()
