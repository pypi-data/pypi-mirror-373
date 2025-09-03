import argparse
import sys
from typing import Dict, List, Optional

from runbooks.finops.cli import main as cli_main_entry


def main() -> int:
    """Entry point for the finops submodule when run directly."""
    return cli_main_entry()


if __name__ == "__main__":
    sys.exit(main())
