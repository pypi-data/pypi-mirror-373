#!/usr/bin/env python3

"""
AWS Security Baseline Tester Script

Date: 2025-01-10
Version: 1.1.0

This script evaluates AWS account security configurations against a baseline checklist
and generates a multilingual report in HTML format.

Compatible with both local (via pip or Docker) and AWS Lambda environments.
"""

import argparse
import sys

from runbooks.common.rich_utils import (
    console,
    create_panel,
    print_error,
    print_info,
    print_success,
    print_warning,
)
from runbooks.utils.logger import configure_logger

from .security_baseline_tester import SecurityBaselineTester

## ✅ Configure Logger
logger = configure_logger(__name__)


# ==============================
# Parse Command-Line Arguments
# ==============================
def parse_arguments():
    """
    Parses command-line arguments for the security baseline tester.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="AWS Security Baseline Tester - Evaluate your AWS account's security configuration."
    )
    parser.add_argument(
        "--profile",
        default="default",
        help="AWS IAM profile to use for authentication (default: 'default').",
    )
    parser.add_argument(
        "--language",
        choices=["EN", "JP", "KR", "VN"],
        default="EN",
        help="Language for the Security Baseline Report (default: 'EN').",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Custom output directory for HTML results (default: ./results).",
    )
    return parser.parse_args()


# ==============================
# Main Function
# ==============================
def main():
    """
    Main entry point for the AWS Security Baseline Tester.
    """
    try:
        args = parse_arguments()

        # Display startup information with Rich formatting
        startup_info = f"""[bold cyan]AWS Security Baseline Tester[/bold cyan]

[green]Configuration:[/green]
  [cyan]AWS Profile:[/cyan] {args.profile}
  [cyan]Language:[/cyan] {args.language}
  [cyan]Output Directory:[/cyan] {args.output or "./results"}
  
[dim]Starting comprehensive security assessment...[/dim]"""

        console.print(create_panel(startup_info, title="🔒 Security Baseline Tester", border_style="cyan"))

        print_info("Initializing AWS Security Baseline Tester...")
        print_info(f"Using AWS profile: {args.profile}")
        print_info(f"Report language: {args.language}")
        print_info(f"Output directory: {args.output or './results'}")

        ## Instantiate and run the Security Baseline Tester
        tester = SecurityBaselineTester(args.profile, args.language, args.output)
        tester.run()

        print_success("AWS Security Baseline testing completed successfully!")

    except Exception as e:
        print_error(f"An unexpected error occurred: {e}", exception=e)
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
