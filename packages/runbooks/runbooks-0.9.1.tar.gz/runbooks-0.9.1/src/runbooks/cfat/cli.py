"""
Direct CLI interface for Cloud Foundations Assessment Tool (CFAT).

This module provides a standalone CLI entry point for CFAT that can be
accessed directly via 'cfat' or 'runbooks-cfat' commands.

This provides a focused interface for users who primarily use CFAT
and want direct access without the broader runbooks CLI structure.
"""

import sys

import click
from loguru import logger

from runbooks.cfat import __version__ as cfat_version
from runbooks.main import assess as main_assess


@click.group(invoke_without_command=True)
@click.version_option(version=cfat_version)
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--profile", default="default", help="AWS profile to use")
@click.option("--region", help="AWS region (overrides profile region)")
@click.pass_context
def main(ctx, debug, profile, region):
    """
    Cloud Foundations Assessment Tool (CFAT) - Direct CLI Access.

    Enterprise-grade AWS Cloud Foundations assessment with comprehensive
    reporting, parallel execution, and compliance framework alignment.

    This tool evaluates AWS accounts against Cloud Foundations best practices
    and generates actionable findings with remediation guidance.

    Examples:
        cfat assess --output html --severity CRITICAL
        cfat assess --compliance-framework SOC2 --export-jira findings.csv
        cfat assess --serve-web --web-port 8080

    For full documentation: https://cloudops.oceansoft.io/runbooks/cfat/
    """
    # Initialize context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["profile"] = profile
    ctx.obj["region"] = region

    # Setup logging
    if debug:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    # Show help if no command provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Import and register the assess command from main CLI
# This reuses the enhanced assess command with all its features
main.add_command(main_assess, name="assess")


@main.command()
@click.pass_context
def version(ctx):
    """Show CFAT version information."""
    click.echo(f"Cloud Foundations Assessment Tool (CFAT) version {cfat_version}")
    click.echo("Part of CloudOps Runbooks - Enterprise CloudOps Automation")
    click.echo("Documentation: https://cloudops.oceansoft.io/runbooks/cfat/")


@main.command()
@click.pass_context
def status(ctx):
    """Show CFAT status and configuration."""
    click.echo("🔍 Cloud Foundations Assessment Tool Status")
    click.echo(f"Version: {cfat_version}")
    click.echo(f"Profile: {ctx.obj['profile']}")
    click.echo(f"Region: {ctx.obj['region'] or 'Default from profile'}")
    click.echo(f"Debug: {ctx.obj['debug']}")

    # Show available assessment categories
    click.echo("\n📋 Available Assessment Categories:")
    categories = ["iam", "vpc", "ec2", "cloudtrail", "config", "organizations", "cloudformation"]
    for category in categories:
        click.echo(f"  • {category}")

    # Show available output formats
    click.echo("\n📄 Available Output Formats:")
    formats = ["console", "html", "csv", "json", "markdown", "all"]
    for fmt in formats:
        click.echo(f"  • {fmt}")

    # Show available exporters
    click.echo("\n🔗 Available Export Integrations:")
    exporters = ["jira", "asana", "servicenow"]
    for exporter in exporters:
        click.echo(f"  • {exporter}")


if __name__ == "__main__":
    main()
