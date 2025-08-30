#!/usr/bin/env python3
"""
Rich Library Utilities for CloudOps Runbooks Platform

This module provides centralized Rich components and styling for consistent,
beautiful terminal output across all CloudOps Runbooks modules.

Features:
- Custom CloudOps theme and color schemes
- Reusable UI components (headers, footers, panels)
- Standard progress bars and spinners
- Consistent table styles
- Error/warning/success message formatting
- Tree displays for hierarchical data
- Layout templates for complex displays

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
from rich.rule import Rule
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich.tree import Tree

# CloudOps Custom Theme
CLOUDOPS_THEME = Theme(
    {
        "info": "cyan",
        "success": "green bold",
        "warning": "yellow bold",
        "error": "red bold",
        "critical": "red bold reverse",
        "highlight": "bright_blue bold",
        "header": "bright_cyan bold",
        "subheader": "cyan",
        "dim": "dim white",
        "resource": "bright_magenta",
        "cost": "bright_green",
        "security": "bright_red",
        "compliance": "bright_yellow",
    }
)

# Initialize console with custom theme
console = Console(theme=CLOUDOPS_THEME)

# Status indicators
STATUS_INDICATORS = {
    "success": "🟢",
    "warning": "🟡",
    "error": "🔴",
    "info": "🔵",
    "pending": "⚪",
    "running": "🔄",
    "stopped": "⏹️",
    "critical": "🚨",
}


def get_console() -> Console:
    """Get the themed console instance."""
    return console


def get_context_aware_console():
    """
    Get a context-aware console that adapts to CLI vs Jupyter environments.

    This function is a bridge to the context_logger module to maintain
    backward compatibility while enabling context awareness.

    Returns:
        Context-aware console instance
    """
    try:
        from runbooks.common.context_logger import get_context_console

        return get_context_console()
    except ImportError:
        # Fallback to regular console if context_logger not available
        return console


def print_header(title: str, version: str = "0.7.8") -> None:
    """
    Print a consistent header for all modules.

    Args:
        title: Module title
        version: Module version
    """
    header_text = Text()
    header_text.append("CloudOps Runbooks ", style="header")
    header_text.append(f"| {title} ", style="subheader")
    header_text.append(f"v{version}", style="dim")

    console.print()
    console.print(Panel(header_text, box=box.DOUBLE, style="header"))
    console.print()


def print_banner() -> None:
    """Print the CloudOps Runbooks ASCII banner."""
    banner = r"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   _____ _                 _  ____              ____            ║
    ║  / ____| |               | |/ __ \            |  _ \           ║
    ║ | |    | | ___  _   _  __| | |  | |_ __  ___  | |_) |_   _ __ ║
    ║ | |    | |/ _ \| | | |/ _` | |  | | '_ \/ __| |  _ <| | | '_ \ ║
    ║ | |____| | (_) | |_| | (_| | |__| | |_) \__ \ | |_) | |_| | | |║
    ║  \_____|_|\___/ \__,_|\__,_|\____/| .__/|___/ |____/ \__,_|_| |║
    ║                                   | |                          ║
    ║   Enterprise AWS Automation      |_|         Platform v0.7.8   ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="header")


def create_table(
    title: Optional[str] = None,
    columns: List[Dict[str, Any]] = None,
    show_header: bool = True,
    show_footer: bool = False,
    box_style: Any = box.ROUNDED,
    title_style: str = "header",
) -> Table:
    """
    Create a consistent styled table.

    Args:
        title: Table title
        columns: List of column definitions [{"name": "Col1", "style": "cyan", "justify": "left"}]
        show_header: Show header row
        show_footer: Show footer row
        box_style: Rich box style
        title_style: Style for title

    Returns:
        Configured Table object
    """
    table = Table(
        title=title,
        show_header=show_header,
        show_footer=show_footer,
        box=box_style,
        title_style=title_style,
        header_style="bold",
        row_styles=["none", "dim"],  # Alternating row colors
    )

    if columns:
        for col in columns:
            table.add_column(
                col.get("name", ""),
                style=col.get("style", ""),
                justify=col.get("justify", "left"),
                no_wrap=col.get("no_wrap", False),
            )

    return table


def create_progress_bar(description: str = "Processing") -> Progress:
    """
    Create a consistent progress bar.

    Args:
        description: Progress bar description

    Returns:
        Configured Progress object
    """
    return Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, style="cyan", complete_style="green"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )


def print_status(message: str, status: str = "info") -> None:
    """
    Print a status message with appropriate styling and indicator.

    Args:
        message: Status message
        status: Status type (success, warning, error, info, critical)
    """
    indicator = STATUS_INDICATORS.get(status, "")
    style = status if status in ["success", "warning", "error", "critical", "info"] else "info"
    console.print(f"{indicator} {message}", style=style)


def print_error(message: str, exception: Optional[Exception] = None) -> None:
    """
    Print an error message with optional exception details.

    Args:
        message: Error message
        exception: Optional exception object
    """
    console.print(f"{STATUS_INDICATORS['error']} {message}", style="error")
    if exception:
        console.print(f"    Details: {str(exception)}", style="dim")


def print_success(message: str) -> None:
    """
    Print a success message.

    Args:
        message: Success message
    """
    console.print(f"{STATUS_INDICATORS['success']} {message}", style="success")


def print_warning(message: str) -> None:
    """
    Print a warning message.

    Args:
        message: Warning message
    """
    console.print(f"{STATUS_INDICATORS['warning']} {message}", style="warning")


def print_info(message: str) -> None:
    """
    Print an info message.

    Args:
        message: Info message
    """
    console.print(f"{STATUS_INDICATORS['info']} {message}", style="info")


def create_tree(label: str, style: str = "cyan") -> Tree:
    """
    Create a tree for hierarchical display.

    Args:
        label: Root label
        style: Tree style

    Returns:
        Tree object
    """
    return Tree(label, style=style, guide_style="dim")


def print_separator(label: Optional[str] = None, style: str = "dim") -> None:
    """
    Print a separator line.

    Args:
        label: Optional label for separator
        style: Separator style
    """
    if label:
        console.print(Rule(label, style=style))
    else:
        console.print(Rule(style=style))


def create_panel(
    content: Any,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    border_style: str = "cyan",
    padding: int = 1,
) -> Panel:
    """
    Create a panel for highlighting content.

    Args:
        content: Panel content
        title: Panel title
        subtitle: Panel subtitle
        border_style: Border color/style
        padding: Internal padding

    Returns:
        Panel object
    """
    return Panel(
        content, title=title, subtitle=subtitle, border_style=border_style, padding=(padding, padding), expand=False
    )


def format_cost(amount: float, currency: str = "USD") -> Text:
    """
    Format a cost value with appropriate styling.

    Args:
        amount: Cost amount
        currency: Currency code

    Returns:
        Formatted Text object
    """
    text = Text()
    symbol = "$" if currency == "USD" else currency
    if amount >= 10000:
        text.append(f"{symbol}{amount:,.2f}", style="cost bold")
    elif amount >= 1000:
        text.append(f"{symbol}{amount:,.2f}", style="cost")
    else:
        text.append(f"{symbol}{amount:,.2f}", style="dim")
    return text


def format_resource_count(count: int, resource_type: str) -> Text:
    """
    Format a resource count with appropriate styling.

    Args:
        count: Resource count
        resource_type: Type of resource

    Returns:
        Formatted Text object
    """
    text = Text()
    if count == 0:
        text.append(f"{count} {resource_type}", style="dim")
    elif count > 100:
        text.append(f"{count} {resource_type}", style="warning")
    else:
        text.append(f"{count} {resource_type}", style="resource")
    return text


def create_display_profile_name(profile_name: str, max_length: int = 25, context_aware: bool = True) -> str:
    """
    Create user-friendly display version of AWS profile names for better readability.

    This function intelligently truncates long enterprise profile names while preserving
    meaningful information for identification. Full names remain available for AWS API calls.

    Examples:
        'ams-admin-Billing-ReadOnlyAccess-909135376185' → 'ams-admin-Billing-9091...'
        'ams-centralised-ops-ReadOnlyAccess-335083429030' → 'ams-centralised-ops-3350...'
        'short-profile' → 'short-profile' (no truncation needed)

    Args:
        profile_name: Full AWS profile name
        max_length: Maximum display length (default 25 for table formatting)
        context_aware: Whether to adapt truncation based on execution context

    Returns:
        User-friendly display name for console output
    """
    if not profile_name or len(profile_name) <= max_length:
        return profile_name

    # Context-aware length adjustment
    if context_aware:
        try:
            from runbooks.common.context_logger import ExecutionContext, get_context_config

            config = get_context_config()

            if config.context == ExecutionContext.JUPYTER:
                # Shorter names for notebook tables
                max_length = min(max_length, 20)
            elif config.context == ExecutionContext.CLI:
                # Slightly longer for CLI terminals
                max_length = min(max_length + 5, 30)
        except ImportError:
            # Fallback if context_logger not available
            pass

    # Smart truncation strategy for AWS profile patterns
    # Common patterns: ams-{type}-{service}-{permissions}-{account_id}

    if "-" in profile_name:
        parts = profile_name.split("-")

        # Strategy 1: Keep meaningful prefix + account ID suffix
        if len(parts) >= 4 and parts[-1].isdigit():
            # Enterprise pattern: ams-admin-Billing-ReadOnlyAccess-909135376185
            account_id = parts[-1]
            prefix_parts = parts[:-2]  # Skip permissions part for brevity

            prefix = "-".join(prefix_parts)
            account_short = account_id[:4]  # First 4 digits of account ID

            truncated = f"{prefix}-{account_short}..."

            if len(truncated) <= max_length:
                return truncated

        # Strategy 2: Keep first few meaningful parts
        meaningful_parts = []
        current_length = 0

        for part in parts:
            # Skip common noise words but keep meaningful ones
            if part.lower() in ["readonlyaccess", "fullaccess", "access"]:
                continue

            part_with_sep = f"{part}-" if meaningful_parts else part
            if current_length + len(part_with_sep) + 3 <= max_length:  # +3 for "..."
                meaningful_parts.append(part)
                current_length += len(part_with_sep)
            else:
                break

        if len(meaningful_parts) >= 2:
            return f"{'-'.join(meaningful_parts)}..."

    # Strategy 3: Simple prefix truncation with ellipsis
    return f"{profile_name[: max_length - 3]}..."


def format_profile_name(profile_name: str, style: str = "cyan", display_max_length: int = 25) -> Text:
    """
    Format profile name with consistent styling and intelligent truncation.

    This function creates a Rich Text object with:
    - Smart truncation for display readability
    - Consistent styling across all modules
    - Hover-friendly formatting (full name in tooltip would be future enhancement)

    Args:
        profile_name: AWS profile name
        style: Rich style for the profile name
        display_max_length: Maximum length for display

    Returns:
        Rich Text object with formatted profile name
    """
    display_name = create_display_profile_name(profile_name, display_max_length)

    text = Text()

    # Add visual indicators for truncated names
    if display_name.endswith("..."):
        # Truncated name - use slightly different style
        text.append(display_name, style=f"{style} italic")
    else:
        # Full name - normal style
        text.append(display_name, style=style)

    return text


def format_account_name(
    account_name: str, account_id: str, style: str = "bold bright_white", max_length: int = 35
) -> str:
    """
    Format account name with ID for consistent enterprise display in tables.

    This function provides consistent account display formatting across all FinOps dashboards:
    - Account name with intelligent truncation
    - Account ID as secondary line for identification
    - Rich markup for professional presentation

    Args:
        account_name: Resolved account name from Organizations API
        account_id: AWS account ID
        style: Rich style for the account name
        max_length: Maximum display length for account name

    Returns:
        Formatted display string with Rich markup

    Example:
        "Data Management"
        "123456789012"
    """
    if account_name and account_name != account_id and len(account_name.strip()) > 0:
        # We have a resolved account name - format with both name and ID
        display_name = account_name if len(account_name) <= max_length else account_name[: max_length - 3] + "..."
        return f"[{style}]{display_name}[/]\n[dim]{account_id}[/]"
    else:
        # No resolved name available - show account ID prominently
        return f"[{style}]{account_id}[/]"


def create_layout(sections: Dict[str, Any]) -> Layout:
    """
    Create a layout for complex displays.

    Args:
        sections: Dictionary of layout sections

    Returns:
        Layout object
    """
    layout = Layout()

    # Example layout structure
    if "header" in sections:
        layout.split_column(Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3))
        layout["header"].update(sections["header"])

    if "body" in sections:
        if isinstance(sections["body"], dict):
            layout["body"].split_row(*[Layout(name=k) for k in sections["body"].keys()])
            for key, content in sections["body"].items():
                layout["body"][key].update(content)
        else:
            layout["body"].update(sections["body"])

    if "footer" in sections:
        layout["footer"].update(sections["footer"])

    return layout


def print_json(data: Dict[str, Any], title: Optional[str] = None) -> None:
    """
    Print JSON data with syntax highlighting.

    Args:
        data: JSON data to display
        title: Optional title
    """
    import json

    json_str = json.dumps(data, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
    if title:
        console.print(Panel(syntax, title=title, border_style="cyan"))
    else:
        console.print(syntax)


def print_markdown(text: str) -> None:
    """
    Print markdown formatted text.

    Args:
        text: Markdown text
    """
    md = Markdown(text)
    console.print(md)


def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Get user confirmation with styled prompt.

    Args:
        prompt: Confirmation prompt
        default: Default value if user just presses enter

    Returns:
        User's confirmation choice
    """
    default_text = "[Y/n]" if default else "[y/N]"
    console.print(f"\n{STATUS_INDICATORS['info']} {prompt} {default_text}: ", style="info", end="")

    response = input().strip().lower()
    if not response:
        return default
    return response in ["y", "yes"]


def create_columns(items: List[Any], equal: bool = True, expand: bool = True) -> Columns:
    """
    Create columns for side-by-side display.

    Args:
        items: List of items to display in columns
        equal: Equal width columns
        expand: Expand to full width

    Returns:
        Columns object
    """
    return Columns(items, equal=equal, expand=expand, padding=(0, 2))


# Export all public functions and constants
__all__ = [
    "CLOUDOPS_THEME",
    "STATUS_INDICATORS",
    "console",
    "get_console",
    "get_context_aware_console",
    "print_header",
    "print_banner",
    "create_table",
    "create_progress_bar",
    "print_status",
    "print_error",
    "print_success",
    "print_warning",
    "print_info",
    "create_tree",
    "print_separator",
    "create_panel",
    "format_cost",
    "format_resource_count",
    "create_display_profile_name",
    "format_profile_name",
    "format_account_name",
    "create_layout",
    "print_json",
    "print_markdown",
    "confirm_action",
    "create_columns",
]
